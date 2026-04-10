"""
Governance Check 1: Policy Enforcement (Agent OS)
===================================================
Now respects enforcement mode:
  ENFORCE = block denied tools
  MONITOR = log but allow denied tools
"""

from agent_os.policies import PolicyEvaluator, PolicyDocument, PolicyRule, PolicyAction
from agent_os.policies.schema import PolicyCondition, PolicyOperator
from research_agent.audit import log_event
from research_agent.governance.config import is_enforce_mode

# ── Define policy rules (same as Section 7) ──
_policy = PolicyDocument(
    version="1.0",
    name="research-analyst-policy",
    description="Policy for the research analyst agent",
    rules=[
        PolicyRule(
            name="allow-web-search",
            condition=PolicyCondition(field="tool_name", operator=PolicyOperator.EQ, value="web_search"),
            action=PolicyAction.ALLOW, priority=10,
        ),
        PolicyRule(
            name="allow-read-file",
            condition=PolicyCondition(field="tool_name", operator=PolicyOperator.EQ, value="read_file"),
            action=PolicyAction.ALLOW, priority=10,
        ),
        PolicyRule(
            name="allow-write-report",
            condition=PolicyCondition(field="tool_name", operator=PolicyOperator.EQ, value="write_report"),
            action=PolicyAction.ALLOW, priority=10,
        ),
        PolicyRule(
            name="block-shell-execution",
            condition=PolicyCondition(
                field="tool_name", operator=PolicyOperator.IN,
                value=["execute_shell", "run_shell", "eval", "exec"],
            ),
            action=PolicyAction.DENY, priority=100,
            message="Shell execution is not allowed by governance policy",
        ),
    ],
)

_evaluator = PolicyEvaluator(policies=[_policy])


def check_policy(agent_id: str, tool_name: str) -> dict | None:
    """Check if a tool call is allowed by policy."""
    decision = _evaluator.evaluate({"tool_name": tool_name, "agent_id": agent_id})

    if decision.allowed:
        log_event(
            event_type="POLICY_ALLOWED",
            tool_name=tool_name,
            verdict="ALLOWED",
            reason=decision.reason,
        )
        return None

    # Tool is denied by policy
    if is_enforce_mode():
        log_event(
            event_type="POLICY_DENIED",
            tool_name=tool_name,
            verdict="BLOCKED",
            reason=f"[ENFORCE] {decision.reason}",
            extra={"matched_rule": decision.matched_rule},
        )
        return {
            "status": "blocked_by_governance",
            "tool": tool_name,
            "reason": f"Governance policy denied this tool. {decision.reason}",
        }
    else:
        log_event(
            event_type="POLICY_VIOLATION_MONITOR",
            tool_name=tool_name,
            verdict="WARN",
            reason=f"[MONITOR] Would be blocked in ENFORCE mode. {decision.reason}",
            extra={"matched_rule": decision.matched_rule},
        )
        return None  # Allow — monitoring only