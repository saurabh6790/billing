# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt
"""Shared helpers for press_billing tests."""

import frappe

DEFAULT_RESOURCES = [
	{
		"resource_type": "compute",
		"unit": "vCPU",
		"quantity_included": 2,
		"price_per_unit": 10,
		"billing_type": "fixed",
		"billing_interval": "monthly",
	},
	{
		"resource_type": "memory",
		"unit": "GB",
		"quantity_included": 4,
		"price_per_unit": 5,
		"billing_type": "fixed",
		"billing_interval": "monthly",
	},
]


def make_plan(name, resources=None, **kwargs):
	"""Create (or replace) a Plan with the given resources and return its name."""
	if frappe.db.exists("Plan", name):
		frappe.delete_doc("Plan", name, force=True)

	doc = frappe.get_doc(
		{
			"doctype": "Plan",
			"__newname": name,
			"title": kwargs.get("title", name),
			"plan_type": kwargs.get("plan_type", "base"),
			"billing_cycle": kwargs.get("billing_cycle", "monthly"),
			"currency": kwargs.get("currency", "USD"),
			"is_active": kwargs.get("is_active", 1),
			"plan_resources": resources if resources is not None else DEFAULT_RESOURCES,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name
