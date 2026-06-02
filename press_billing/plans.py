# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt
"""Live plan pricing reads.

Pricing is read live at purchase (human pace), locked at provision, and frozen
for billing (machine pace). This module serves the first role only.
"""

import frappe


@frappe.whitelist()
def get_plan_pricing(plan: str, currency: str | None = None, cluster: str | None = None) -> dict:
	"""Return the live catalog snapshot for a bundle.

	With a currency (and optional cluster) the applicable rate is resolved
	(most-specific region match, else global). Never cached as authoritative.
	"""
	doc = frappe.get_doc("Plan", plan)
	return doc.as_pricing(currency=currency, cluster=cluster)
