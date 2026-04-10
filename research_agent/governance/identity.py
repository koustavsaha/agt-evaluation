"""
Agent Identity Manager
========================
Uses AGT's real AgentIdentity for DID + Ed25519 signing.
Uses AGT's real RewardEngine for multi-dimensional trust scoring.

Discovery note: The README shows trust_score as a property of
AgentIdentity. In the installed Python package (v3.0.x), it is
NOT on AgentIdentity. The actual trust scoring system lives in
agentmesh.reward.engine.RewardEngine — a much more sophisticated
multi-dimensional weighted scoring system than the README describes.
"""

from agentmesh import AgentIdentity
from agentmesh.reward.engine import RewardEngine
from research_agent.audit import log_event

# ── Create the agent's cryptographic identity (AGT's real API) ──
identity = AgentIdentity.create(
    name="research-analyst",
    sponsor="eval-admin@company.com",
    capabilities=["read:web", "read:files", "write:reports"],
)
agent_did = str(identity.did)  # RewardEngine needs a plain string, not AgentDID object

# ── Create the multi-dimensional trust scoring engine ──
reward_engine = RewardEngine()

print(f"[IDENTITY] Agent DID: {identity.did}")
print(f"[IDENTITY] Status: {identity.status}")
initial_score = reward_engine.get_agent_score(agent_did)
print(f"[IDENTITY] Trust: score={initial_score.total_score}, tier={initial_score.tier}")

MINIMUM_TRUST_SCORE = 200


def get_identity():
    """Return the agent's identity object."""
    return identity


def get_trust_score():
    """Get the current composite trust score (0-1000)."""
    score = reward_engine.get_agent_score(agent_did)
    return score.total_score


def get_trust_tier():
    """Get the current trust tier (probationary/standard/trusted/verified)."""
    score = reward_engine.get_agent_score(agent_did)
    return score.tier


def check_trust(tool_name: str) -> dict | None:
    """
    Check if the agent's trust score is above the minimum threshold.

    Returns:
        None if trust is sufficient (proceed to next check).
        A dict if trust is too low (block all tool calls).
    """
    score = reward_engine.get_agent_score(agent_did)
    if score.total_score >= MINIMUM_TRUST_SCORE:
        return None  # Trust OK — proceed

    log_event(
        event_type="TRUST_TOO_LOW",
        tool_name=tool_name,
        verdict="DENIED",
        reason=f"Trust score {score.total_score} ({score.tier}) below minimum {MINIMUM_TRUST_SCORE}",
        extra={"trust_score": score.total_score, "tier": score.tier},
    )
    return {
        "status": "blocked_by_governance",
        "reason": f"Agent trust score ({score.total_score}, tier: {score.tier}) "
                  f"is below minimum ({MINIMUM_TRUST_SCORE}). All tool calls are blocked.",
    }


def record_policy_violation(policy_name: str = "unknown"):
    """Called when a policy check denies a tool call. Degrades policy_compliance dimension."""
    reward_engine.record_policy_compliance(agent_did, compliant=False, policy_name=policy_name)
    score = reward_engine.get_agent_score(agent_did)
    log_event(
        event_type="TRUST_DECREASED",
        verdict="PENALTY",
        reason=f"Policy violation → score={score.total_score}, tier={score.tier}",
        extra={"trust_score": score.total_score, "tier": score.tier, "policy": policy_name},
    )


def record_security_violation(event_type: str = "injection_attempt"):
    """Called when an injection or security event is detected. Degrades security_posture."""
    reward_engine.record_security_event(agent_did, within_boundary=False, event_type=event_type)
    score = reward_engine.get_agent_score(agent_did)
    log_event(
        event_type="TRUST_SECURITY_PENALTY",
        verdict="PENALTY",
        reason=f"Security violation ({event_type}) → score={score.total_score}, tier={score.tier}",
        extra={"trust_score": score.total_score, "tier": score.tier},
    )


def record_successful_tool_call():
    """Called when a tool call succeeds. Improves policy_compliance dimension."""
    reward_engine.record_policy_compliance(agent_did, compliant=True)


def record_failed_tool_call():
    """Called when a tool call fails. Degrades policy_compliance dimension."""
    reward_engine.record_policy_compliance(agent_did, compliant=False, policy_name="tool_failure")