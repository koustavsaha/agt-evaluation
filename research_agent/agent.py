"""
Research Analyst Agent — Version 4 (Policy + Identity + Trust)
===============================================================
Added: Agent Mesh identity and RewardEngine trust scoring.
Now: policy violations degrade the policy_compliance dimension.
Security events degrade the security_posture dimension.
If composite trust score drops below 200, ALL tools are blocked.
"""

from google.adk.agents import Agent
from research_agent.tools import web_search, read_file, write_report, execute_shell
from research_agent.audit import log_event
from research_agent.governance.checks.policy_check import check_policy
from research_agent.governance.identity import (
    get_identity, get_trust_score, get_trust_tier, check_trust,
    record_policy_violation, record_successful_tool_call, record_failed_tool_call,
)


def before_tool_callback(*, tool, args, tool_context):
    tool_name = tool.name
    tool_input = args
    """Governance checkpoint — fires before every tool call."""
    identity = get_identity()

    # ── Check 1: Trust Score ──
    denial = check_trust(tool_name)
    if denial is not None:
        return denial  # Trust too low — block everything

    # ── Check 2: Policy Enforcement ──
    denial = check_policy(agent_id=str(identity.did), tool_name=tool_name)
    if denial is not None:
        record_policy_violation(policy_name="block-shell-execution")
        return denial

    # All checks passed
    log_event(
        event_type="ALL_CHECKS_PASSED",
        tool_name=tool_name,
        verdict="ALLOWED",
        reason="Identity OK, policy OK",
        extra={"trust_score": get_trust_score(), "tier": get_trust_tier()},
    )
    return None


def after_tool_callback(*, tool, args, tool_context, tool_response):
    tool_name = tool.name
    tool_output = tool_response
    """Post-execution: update trust score and log."""
    is_success = isinstance(tool_output, dict) and tool_output.get("status") != "error"

    if is_success:
        record_successful_tool_call()
    else:
        record_failed_tool_call()

    log_event(
        event_type="TOOL_COMPLETED",
        tool_name=tool_name,
        verdict="SUCCESS" if is_success else "FAILED",
        reason=f"Trust: score={get_trust_score()}, tier={get_trust_tier()}",
        extra={"trust_score": get_trust_score(), "tier": get_trust_tier()},
    )
    return None


root_agent = Agent(
    model="gemini-3-flash-preview",
    name="research_analyst",
    description="A governed research analyst with identity and multi-dimensional trust scoring.",
    instruction=(
        "You are a research analyst with governance controls.\n"
        "If a tool is blocked, explain the restriction to the user.\n"
        "It's okay to try to call a blocked tool more than once."
    ),
    tools=[web_search, read_file, write_report, execute_shell],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)