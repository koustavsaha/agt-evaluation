"""
Governance Check 1: Policy Enforcement (Agent OS)
===================================================
Uses AGT's real PolicyEvaluator with PolicyDocument and PolicyRule.
Evaluates every tool call against allow/deny rules.
If denied → tool call is BLOCKED.
If no rule matches → BLOCKED (catch-all deny rule at lowest priority).
"""

from agent_os.policies import PolicyEvaluator, PolicyDocument, PolicyRule, PolicyAction
from agent_os.policies.schema import PolicyCondition, PolicyOperator
from research_agent.audit import log_event

# ── Define policy rules ──
# Each rule has: a name, a condition (field + operator + value),
# an action (ALLOW or DENY), a priority (higher = evaluated first),
# and a message (shown when the rule triggers).

_policy = PolicyDocument(
    version="1.0",
    name="research-analyst-policy",
    description="Policy for the research analyst agent",
    rules=[
        # Allow safe tools (priority 10)
        PolicyRule(
            name="allow-web-search",
            condition=PolicyCondition(field="tool_name", operator=PolicyOperator.EQ, value="web_search"),
            action=PolicyAction.ALLOW,
            priority=10,
            message="web_search is allowed",
        ),
        PolicyRule(
            name="allow-read-file",
            condition=PolicyCondition(field="tool_name", operator=PolicyOperator.EQ, value="read_file"),
            action=PolicyAction.ALLOW,
            priority=10,
            message="read_file is allowed",
        ),
        PolicyRule(
            name="allow-write-report",
            condition=PolicyCondition(field="tool_name", operator=PolicyOperator.EQ, value="write_report"),
            action=PolicyAction.ALLOW,
            priority=10,
            message="write_report is allowed",
        ),

        # Block dangerous tools (priority 100 — highest, wins over allow)
        PolicyRule(
            name="block-shell-execution",
            condition=PolicyCondition(
                field="tool_name",
                operator=PolicyOperator.IN,
                value=["execute_shell", "run_shell", "eval", "exec"],
            ),
            action=PolicyAction.DENY,
            priority=100,
            message="Shell execution is not allowed by governance policy",
        ),
    ],
)

# Create the evaluator with our policy
_evaluator = PolicyEvaluator(policies=[_policy])


def check_policy(agent_id: str, tool_name: str) -> dict | None:
    """
    Check if a tool call is allowed by policy.

    Args:
        agent_id: The agent's identifier.
        tool_name: The name of the tool being called.

    Returns:
        None if ALLOWED (tool should proceed).
        A dict if BLOCKED (dict becomes the tool's "result" — agent sees denial message).
    """
    # Evaluate the tool call against our policy rules
    decision = _evaluator.evaluate({"tool_name": tool_name, "agent_id": agent_id})

    if decision.allowed:
        log_event(
            event_type="POLICY_ALLOWED",
            tool_name=tool_name,
            verdict="ALLOWED",
            reason=decision.reason,
        )
        return None  # None = proceed

    else:
        log_event(
            event_type="POLICY_DENIED",
            tool_name=tool_name,
            verdict="DENIED",
            reason=decision.reason,
            extra={"matched_rule": decision.matched_rule},
        )
        # Return a dict — this becomes the tool's "result"
        # The LLM will see this message instead of the tool's actual output
        return {
            "status": "blocked_by_governance",
            "tool": tool_name,
            "reason": f"Governance policy denied this tool. {decision.reason}",
            "suggestion": "Try using an allowed tool instead (web_search, read_file, write_report).",
        }