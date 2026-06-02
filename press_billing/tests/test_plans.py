# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase

from press_billing.plans import get_plan_pricing
from press_billing.tests.utils import make_plan


class TestGetPlanPricing(IntegrationTestCase):
	def test_returns_live_display_price_for_plan(self):
		# 2 vCPU @ 10 + 4 GB @ 5 = 40
		make_plan("plan-test-2vcpu")

		pricing = get_plan_pricing(plan="plan-test-2vcpu")

		self.assertEqual(pricing["plan"], "plan-test-2vcpu")
		self.assertEqual(pricing["currency"], "USD")
		self.assertEqual(pricing["display_price"], 40)


class TestPlanIdentity(IntegrationTestCase):
	def test_price_edit_does_not_fork_a_new_plan(self):
		name = make_plan("plan-test-price-edit")
		count_before = frappe.db.count("Plan")

		plan = frappe.get_doc("Plan", name)
		plan.plan_resources[0].price_per_unit = 99
		plan.save(ignore_permissions=True)

		# Same identity, no proliferation; live price reflects the edit.
		self.assertEqual(frappe.db.count("Plan"), count_before)
		self.assertEqual(get_plan_pricing(plan=name)["display_price"], 99 * 2 + 5 * 4)
