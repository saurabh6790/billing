# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt
"""UPI Autopay mandate lifecycle (issue #08).

The mandate ceiling is structurally tied to the trust-tier cap: a mandate is
authorised with max_amount = the team's current cap, so a bill can never exceed
it. A tier promotion that raises the cap requires customer re-consent
(re-authorisation); until then the team is held at the old ceiling.
"""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import frappe
from frappe.tests import IntegrationTestCase

from press_billing import mandates
from press_billing.entitlements import recompute_trust_tier
from press_billing.tests.test_entitlements import make_ladder

TEAM = "team-mandate"
GATEWAY = "GW-Mandate-Razorpay"


def make_gateway():
	if frappe.db.exists("Payment Gateway", GATEWAY):
		frappe.delete_doc("Payment Gateway", GATEWAY, force=True)
	frappe.get_doc(
		{
			"doctype": "Payment Gateway",
			"__newname": GATEWAY,
			"title": "Razorpay (Mandate Test)",
			"adapter_key": "razorpay",
			"currency": "INR",
			"api_key": "rzp_test_key",
			"api_secret": "rzp_test_secret",
			"webhook_secret": "rzp_whsec",
			"is_enabled": 1,
			"supports_mandates": 1,
		}
	).insert(ignore_permissions=True)


@contextmanager
def stub_adapter(signature_ok=True):
	"""Replace the resolved GatewayAdapter with a mock so no SDK is touched."""
	adapter = MagicMock()
	adapter.setup_payment_method.return_value = {
		"order_id": "order_mandate",
		"customer_id": "cust_x",
		"key_id": "rzp_test_key",
	}
	adapter.verify_payment_signature.return_value = signature_ok
	adapter.cancel_mandate.return_value = True
	with patch("press_billing.gateways.registry.get_adapter", return_value=adapter):
		yield adapter


class MandateTestBase(IntegrationTestCase):
	def setUp(self):
		make_ladder()
		make_gateway()
		for name in frappe.get_all(
			"Payment Method", filters={"team": TEAM}, pluck="name"
		):
			frappe.delete_doc("Payment Method", name, force=True)
		if frappe.db.exists("Trust Tier", TEAM):
			frappe.delete_doc("Trust Tier", TEAM, force=True)
		# Entry tier: t0 cap = 100.
		recompute_trust_tier(TEAM, paid_invoice_count=0, cumulative_paid=0)


class TestMandateSetup(MandateTestBase):
	def test_setup_locks_ceiling_to_tier_cap(self):
		with stub_adapter() as adapter:
			result = mandates.setup_mandate(TEAM, GATEWAY, customer_id="cust_x")

		# The mandate order was authorised at the team's current cap (t0 = 100).
		args, kwargs = adapter.setup_payment_method.call_args
		self.assertEqual(args[1]["max_amount"], 100)

		method = frappe.get_doc("Payment Method", result["payment_method"])
		self.assertEqual(method.method_type, "upi_autopay")
		self.assertEqual(method.status, "pending_validation")
		self.assertEqual(method.mandate_max_amount, 100)
		self.assertIn("order_id", result)

	def test_confirm_valid_signature_activates(self):
		with stub_adapter(signature_ok=True):
			result = mandates.setup_mandate(TEAM, GATEWAY, customer_id="cust_x")
			method = mandates.confirm_mandate(
				result["payment_method"],
				{"razorpay_token_id": "token_live", "razorpay_signature": "s"},
			)
		self.assertEqual(method.status, "active")
		self.assertEqual(method.gateway_method_id, "token_live")
		self.assertTrue(method.validated_at)

	def test_confirm_invalid_signature_fails(self):
		with stub_adapter(signature_ok=False):
			result = mandates.setup_mandate(TEAM, GATEWAY, customer_id="cust_x")
			with self.assertRaises(frappe.ValidationError):
				mandates.confirm_mandate(result["payment_method"], {"razorpay_signature": "bad"})
		method = frappe.get_doc("Payment Method", result["payment_method"])
		self.assertEqual(method.status, "failed")


class TestMandateReauthorisation(MandateTestBase):
	def _active_mandate(self):
		with stub_adapter(signature_ok=True):
			result = mandates.setup_mandate(TEAM, GATEWAY, customer_id="cust_x")
			mandates.confirm_mandate(
				result["payment_method"],
				{"razorpay_token_id": "token_live", "razorpay_signature": "s"},
			)
		return result["payment_method"]

	def test_promotion_above_ceiling_flags_reauth_and_holds_old_cap(self):
		pm = self._active_mandate()  # ceiling = 100 (t0)

		# Promote to t1 (cap 300) — above the mandate ceiling.
		recompute_trust_tier(TEAM, paid_invoice_count=3, cumulative_paid=300)

		method = frappe.get_doc("Payment Method", pm)
		self.assertTrue(method.reauth_required)
		# Functionally held at the old ceiling until the customer re-consents.
		self.assertEqual(mandates.effective_cap(TEAM), 100)

	def test_reauthorisation_raises_ceiling_and_clears_flag(self):
		pm = self._active_mandate()
		recompute_trust_tier(TEAM, paid_invoice_count=3, cumulative_paid=300)  # cap 300

		with stub_adapter(signature_ok=True):
			reauth = mandates.reauthorise_mandate(pm)
			# New mandate order is requested at the raised cap.
			new_method = frappe.get_doc("Payment Method", reauth["payment_method"])
			self.assertEqual(new_method.mandate_max_amount, 300)
			mandates.confirm_mandate(
				reauth["payment_method"],
				{"razorpay_token_id": "token_new", "razorpay_signature": "s"},
			)

		# Old mandate retired, new ceiling effective, no outstanding re-auth.
		self.assertEqual(mandates.effective_cap(TEAM), 300)
		self.assertEqual(frappe.db.get_value("Payment Method", pm, "status"), "cancelled")
		self.assertFalse(mandates.reauth_pending(TEAM))

	def test_demotion_below_ceiling_needs_no_reauth(self):
		pm = self._active_mandate()  # ceiling 100
		recompute_trust_tier(TEAM, paid_invoice_count=3, cumulative_paid=300)  # cap 300, reauth set
		recompute_trust_tier(TEAM, paid_invoice_count=0, cumulative_paid=0)  # back to t0 cap 100

		method = frappe.get_doc("Payment Method", pm)
		self.assertFalse(method.reauth_required)
		self.assertEqual(mandates.effective_cap(TEAM), 100)


class TestMandateCancel(MandateTestBase):
	def test_cancel_revokes_token_and_sets_status(self):
		with stub_adapter(signature_ok=True) as adapter:
			result = mandates.setup_mandate(TEAM, GATEWAY, customer_id="cust_x")
			mandates.confirm_mandate(
				result["payment_method"],
				{"razorpay_token_id": "token_live", "razorpay_signature": "s"},
			)
			mandates.cancel_mandate(result["payment_method"])
			adapter.cancel_mandate.assert_called_once_with(
				"token_live", customer_reference="cust_x"
			)
		self.assertEqual(
			frappe.db.get_value("Payment Method", result["payment_method"], "status"),
			"cancelled",
		)
