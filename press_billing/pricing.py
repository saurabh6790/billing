# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt
"""Rate resolution — region x currency.

Shared by Plan (bundle) and Add-on. A rate is resolved for a team's billing
currency and the resource's cluster: the most-specific region match wins,
falling back to the global (blank-cluster) row.
"""


def resolve_rate(rate_rows, currency: str, cluster: str | None = None):
	"""Return the rate for (currency, cluster), or None if not configured.

	rate_rows: iterable of rows with .cluster, .currency, .rate.
	"""
	in_currency = [r for r in rate_rows if r.currency == currency]

	if cluster:
		regional = [r for r in in_currency if r.cluster == cluster]
		if regional:
			return regional[0].rate

	for r in in_currency:
		if not r.cluster:
			return r.rate

	return None
