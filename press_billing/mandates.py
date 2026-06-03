# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt
"""UPI Autopay mandate lifecycle (issue #08).

A mandate's ceiling is structurally tied to the team's trust-tier cap: the
mandate is authorised with `max_amount` = the current cap, so a bill can never
exceed it. A tier promotion that raises the cap requires customer re-consent
(re-authorisation); until then the team is held at the old ceiling. Cards are
exempt (off-session, any amount), so only `upi_autopay` methods participate.

This module never imports a gateway SDK directly — it resolves an adapter
through the registry, keeping the gateway seam intact (see gateways/base.py).
"""

import frappe

MANDATE_METHOD = "upi_autopay"


def team_cap(team: str):
	"""Current trust-tier monthly cap for a team (0 when no tier exists yet)."""
	return frappe.db.get_value("Trust Tier", team, "max_spend") or 0


def _adapter(gateway: str):
	from press_billing.gateways.registry import get_adapter

	return get_adapter(frappe.get_doc("Payment Gateway", gateway))


def setup_mandate(team: str, gateway: str, customer_id: str | None = None, is_default: int = 0) -> dict:
	"""Begin UPI Autopay authorisation.

	The ceiling is locked to the team's current trust-tier cap. Returns the
	client-side handles the UI runs Razorpay Checkout against, plus the name of
	the (pending) Payment Method. No money is moved and no token exists yet.
	"""
	cap = team_cap(team)
	handles = _adapter(gateway).setup_payment_method(
		team, {"max_amount": cap, "customer_id": customer_id}
	)

	method = frappe.get_doc(
		{
			"doctype": "Payment Method",
			"team": team,
			"gateway": gateway,
			"method_type": MANDATE_METHOD,
			"status": "pending_validation",
			"mandate_max_amount": cap,
			"mandate_currency": "INR",
			"mandate_customer_id": customer_id,
			"is_default": is_default,
		}
	).insert(ignore_permissions=True)

	return {**handles, "payment_method": method.name}


def confirm_mandate(payment_method: str, callback: dict):
	"""Confirm the Razorpay Checkout callback that authorised the mandate.

	Verifies the checkout-callback signature (distinct from the webhook
	signature), stores the live token, and flips the method to `active`. A new
	active mandate retires any sibling active mandate for the same team+gateway
	(the re-authorisation case), so the higher ceiling cleanly supersedes.
	"""
	method = frappe.get_doc("Payment Method", payment_method)
	adapter = _adapter(method.gateway)

	if not adapter.verify_payment_signature(callback):
		method.status = "failed"
		method.save(ignore_permissions=True)
		frappe.throw("Mandate authorisation signature invalid", frappe.ValidationError)

	method.gateway_method_id = callback.get("razorpay_token_id") or callback.get("token_id")
	method.status = "active"
	method.validated_at = frappe.utils.now_datetime()
	method.reauth_required = 0
	method.save(ignore_permissions=True)

	_retire_superseded_mandates(method)
	return method


def cancel_mandate(payment_method: str):
	"""Revoke the UPI Autopay token at the gateway and mark the method cancelled."""
	method = frappe.get_doc("Payment Method", payment_method)
	if method.gateway_method_id:
		_adapter(method.gateway).cancel_mandate(
			method.gateway_method_id, customer_reference=method.mandate_customer_id
		)
	method.status = "cancelled"
	method.save(ignore_permissions=True)
	return method


def reauthorise_mandate(payment_method: str) -> dict:
	"""Start a fresh authorisation at the team's current (raised) cap.

	The existing mandate stays active at its old ceiling until the new one is
	confirmed — the customer is never left without a working mandate.
	"""
	method = frappe.get_doc("Payment Method", payment_method)
	return setup_mandate(method.team, method.gateway, customer_id=method.mandate_customer_id)


# --- cap reconciliation -----------------------------------------------------


def active_mandate_ceiling(team: str):
	"""Highest ceiling among a team's active mandates (None if none active)."""
	ceilings = frappe.get_all(
		"Payment Method",
		filters={"team": team, "method_type": MANDATE_METHOD, "status": "active"},
		pluck="mandate_max_amount",
	)
	return max(ceilings) if ceilings else None


def effective_cap(team: str):
	"""The cap a mandate team is actually held to: min(tier cap, mandate ceiling).

	A team with no active mandate is bounded purely by its tier cap. A pending
	re-authorisation keeps the ceiling at the *old* value even after the tier
	cap rises, so this naturally returns the old ceiling until re-consent.
	"""
	cap = team_cap(team)
	ceiling = active_mandate_ceiling(team)
	return cap if ceiling is None else min(cap, ceiling)


def reauth_pending(team: str) -> bool:
	"""True if any active mandate is awaiting customer re-authorisation."""
	return bool(
		frappe.get_all(
			"Payment Method",
			filters={
				"team": team,
				"method_type": MANDATE_METHOD,
				"status": "active",
				"reauth_required": 1,
			},
			limit=1,
		)
	)


def reconcile_mandates_to_cap(team: str):
	"""After a tier change, flag/clear re-authorisation on active mandates.

	An active mandate whose ceiling is below the new cap needs re-consent (the
	team is functionally held at the old ceiling until then). A mandate whose
	ceiling already covers the cap — e.g. after a demotion — is cleared.
	Returns the list of mandates newly requiring re-authorisation.
	"""
	cap = team_cap(team)
	flagged = []
	for method in frappe.get_all(
		"Payment Method",
		filters={"team": team, "method_type": MANDATE_METHOD, "status": "active"},
		fields=["name", "mandate_max_amount"],
	):
		needs = cap > (method.mandate_max_amount or 0)
		frappe.db.set_value("Payment Method", method.name, "reauth_required", 1 if needs else 0)
		if needs:
			flagged.append(method.name)
	return flagged


def _retire_superseded_mandates(new_method):
	"""Cancel older active mandates for the same team+gateway once a new mandate
	(typically a re-authorisation at a higher ceiling) goes active."""
	siblings = frappe.get_all(
		"Payment Method",
		filters={
			"team": new_method.team,
			"gateway": new_method.gateway,
			"method_type": MANDATE_METHOD,
			"status": "active",
			"name": ["!=", new_method.name],
		},
		pluck="name",
	)
	for name in siblings:
		cancel_mandate(name)
