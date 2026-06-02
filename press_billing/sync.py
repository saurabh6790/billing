# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt
"""Central -> Agent synchronisation.

Central pushes plan definitions plus a display price to each regional Agent's
Plan Cache. The communication surface is intentionally tiny; this module owns
the Central side of the plan push.
"""

import frappe
import requests

RECEIVE_PLANS_PATH = "/api/method/press_billing_agent.sync.receive_plans"


def _agent_auth_headers() -> dict:
	"""Authorization header for the cluster-scoped Agent API key.

	Credentials live in site config (agent_api_key / agent_api_secret) and are
	never exposed through any customer or admin API.
	"""
	key = frappe.conf.get("agent_api_key")
	secret = frappe.conf.get("agent_api_secret")
	if key and secret:
		return {"Authorization": f"token {key}:{secret}"}
	return {}


@frappe.whitelist()
def push_plans_to_agent(agent_url: str, plans) -> dict:
	"""Push plan identity + composition + display price to an Agent's Plan Cache.

	Cheap and rare (few clusters). The Agent stores these display-only; it
	computes nothing with them.
	"""
	if isinstance(plans, str):
		plans = frappe.parse_json(plans)

	payload = [frappe.get_doc("Plan", name).as_pricing() for name in plans]

	url = agent_url.rstrip("/") + RECEIVE_PLANS_PATH
	response = requests.post(
		url=url,
		json={"plans": payload},
		headers=_agent_auth_headers(),
		timeout=30,
	)
	response.raise_for_status()
	return response.json().get("message")
