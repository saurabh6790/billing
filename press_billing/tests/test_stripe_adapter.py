# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

from contextlib import contextmanager
from unittest.mock import patch

import frappe
import stripe
from frappe.tests import IntegrationTestCase

from press_billing.gateways.base import GatewayUnsupported
from press_billing.gateways.stripe_adapter import StripeAdapter
from press_billing.tests.gateway_contract import GatewayAdapterContract


def make_stripe_gateway(name="GW-Test-Stripe"):
	import frappe

	if frappe.db.exists("Payment Gateway", name):
		frappe.delete_doc("Payment Gateway", name, force=True)
	doc = frappe.get_doc(
		{
			"doctype": "Payment Gateway",
			"__newname": name,
			"title": "Stripe (Test)",
			"adapter_key": "stripe",
			"currency": "USD",
			"api_secret": "sk_test_123",
			"webhook_secret": "whsec_test_123",
			"is_enabled": 1,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc


class TestStripeAdapter(GatewayAdapterContract, IntegrationTestCase):
	def make_adapter(self):
		return StripeAdapter(make_stripe_gateway())

	def webhook_headers(self):
		return {"Stripe-Signature": "t=1,v1=deadbeef"}

	@contextmanager
	def signature_valid(self):
		with patch.object(stripe.Webhook, "construct_event", return_value={"id": "evt_1"}):
			yield

	@contextmanager
	def signature_invalid(self):
		err = stripe.error.SignatureVerificationError("bad sig", "sig-header")
		with patch.object(stripe.Webhook, "construct_event", side_effect=err):
			yield

	def make_charge_inputs(self):
		import frappe

		invoice = frappe._dict(amount=40.0, currency="USD", customer_id="cus_test")
		method = frappe._dict(gateway_method_id="pm_test")
		return invoice, method, "PA-TEST-001"

	@contextmanager
	def charge_succeeds(self, txn_id="txn_ok"):
		import frappe

		intent = frappe._dict(id=txn_id, status="succeeded")
		with patch.object(stripe.PaymentIntent, "create", return_value=intent) as m:
			self._last_create = m
			yield

	@contextmanager
	def charge_declines(self, code="card_declined"):
		err = stripe.error.CardError("Your card was declined.", "card", code)
		with patch.object(stripe.PaymentIntent, "create", side_effect=err) as m:
			self._last_create = m
			yield

	@contextmanager
	def charge_times_out(self):
		err = stripe.error.APIConnectionError("connection timed out")
		with patch.object(stripe.PaymentIntent, "create", side_effect=err) as m:
			self._last_create = m
			yield

	def captured_idempotency_key(self):
		return self._last_create.call_args.kwargs.get("idempotency_key")

	def make_refund_inputs(self):
		import frappe

		payment_attempt = frappe._dict(gateway_transaction_id="pi_charged")
		return payment_attempt, 40.0, "duplicate charge"

	@contextmanager
	def refund_succeeds(self, refund_id="rfnd_ok"):
		import frappe

		refund = frappe._dict(id=refund_id, status="succeeded")
		with patch.object(stripe.Refund, "create", return_value=refund):
			yield

	def parse_event_inputs(self):
		payload = {
			"id": "evt_123",
			"type": "payment_intent.succeeded",
			"data": {"object": {"id": "pi_charged"}},
		}
		# Stripe carries the event id in the body, so headers are irrelevant.
		return payload, {}, "evt_123", "payment_intent.succeeded"

	def setup_inputs(self):
		import frappe

		return "Team-1", {"customer_id": "cus_test"}

	@contextmanager
	def stub_setup(self):
		import frappe

		intent = frappe._dict(id="seti_1", client_secret="seti_1_secret")
		with patch.object(stripe.SetupIntent, "create", return_value=intent):
			yield

	def validation_inputs(self):
		import frappe

		return frappe._dict(gateway_method_id="pm_test", gateway_customer_id="cus_test")

	@contextmanager
	def stub_validation_success(self):
		import frappe

		intent = frappe._dict(id="pi_micro", status="succeeded")
		with (
			patch.object(stripe.PaymentIntent, "create", return_value=intent),
			patch.object(stripe.Refund, "create", return_value=frappe._dict(status="succeeded")),
		):
			yield

	# --- optional, gateway-specific capabilities ----------------------------

	def test_create_customer_returns_id(self):
		adapter = self.make_adapter()
		with patch.object(stripe.Customer, "create", return_value=frappe._dict(id="cus_new")):
			cid = adapter.create_customer(frappe._dict(name="Team-1", user="a@b.com"))
		self.assertEqual(cid, "cus_new")

	def test_get_mandate_status(self):
		adapter = self.make_adapter()
		with patch.object(stripe.Mandate, "retrieve", return_value=frappe._dict(status="active")):
			self.assertEqual(adapter.get_mandate_status("mandate_x"), "active")

	def test_verify_payment_signature_is_unsupported(self):
		adapter = self.make_adapter()
		with self.assertRaises(GatewayUnsupported):
			adapter.verify_payment_signature({})
