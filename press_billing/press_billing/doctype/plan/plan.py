# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class Plan(Document):
	def display_price(self) -> float:
		"""Sum of fixed resources (price_per_unit * quantity_included).

		The headline 'display' price. Display-only: the Agent computes nothing
		with it and billing never reads it (billing reads the price-lock).
		"""
		return sum(
			(r.price_per_unit or 0) * (r.quantity_included or 0)
			for r in self.plan_resources
			if r.billing_type == "fixed"
		)

	def as_pricing(self) -> dict:
		"""Live pricing snapshot: identity + composition + display price.

		Consumed by get_plan_pricing and by the push to an Agent's Plan Cache.
		"""
		return {
			"plan": self.name,
			"title": self.title,
			"plan_type": self.plan_type,
			"billing_cycle": self.billing_cycle,
			"currency": self.currency,
			"is_active": self.is_active,
			"display_price": self.display_price(),
			"resources": [
				{
					"resource_type": r.resource_type,
					"unit": r.unit,
					"quantity_included": r.quantity_included,
					"price_per_unit": r.price_per_unit,
					"metered_rate": r.metered_rate,
					"billing_interval": r.billing_interval,
					"billing_type": r.billing_type,
				}
				for r in self.plan_resources
			],
		}
