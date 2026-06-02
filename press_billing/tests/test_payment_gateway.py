# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase

from press_billing.tests.test_stripe_adapter import make_stripe_gateway


class TestPaymentGatewaySecrets(IntegrationTestCase):
	def test_secrets_are_encrypted_at_rest_but_recoverable(self):
		gw = make_stripe_gateway()

		# Recoverable by the adapter via get_password...
		self.assertEqual(gw.get_password("webhook_secret"), "whsec_test_123")

		# ...but never stored in plaintext.
		stored = frappe.db.get_value("Payment Gateway", gw.name, "webhook_secret")
		self.assertNotEqual(stored, "whsec_test_123")

	def test_password_fields_are_not_exposed_in_document_dict(self):
		gw = make_stripe_gateway()
		# Password fieldtype values are not serialised as plaintext in as_dict.
		self.assertNotEqual(gw.as_dict().get("api_secret"), "sk_test_123")
