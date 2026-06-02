# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt
"""Live plan pricing reads.

Pricing is read live at purchase (human pace), locked at provision, and frozen
for billing (machine pace). This module serves the first role only.
"""

import frappe


@frappe.whitelist()
def get_plan_pricing(plan: str) -> dict:
	"""Return the current (live) Central price for a plan.

	Never cached as authoritative by callers; this is the live catalog price.
	"""
	doc = frappe.get_doc("Plan", plan)
	return {
		"plan": doc.name,
		"title": doc.title,
		"currency": doc.currency,
		"display_price": doc.display_price(),
	}
