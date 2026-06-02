# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from press_billing.pricing import resolve_rate


class Addon(Document):
	def get_rate(self, currency: str, cluster: str | None = None):
		"""Resolved per-unit rate for (currency, cluster). Billed as rate x quantity."""
		return resolve_rate(self.rates, currency, cluster)
