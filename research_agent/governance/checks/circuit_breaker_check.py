"""
Governance Check 4: Circuit Breaker (Agent OS)
================================================
Uses AGT's built-in CircuitBreaker from agent_os.circuit_breaker.
Prevents the agent from repeatedly calling a failing tool.
Each tool gets its own circuit breaker.
"""

from agent_os.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from research_agent.audit import log_event

_config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout_seconds=30.0)

_breakers = {
    "web_search": CircuitBreaker(config=_config),
    "read_file": CircuitBreaker(config=_config),
    "write_report": CircuitBreaker(config=_config),
}


def check_circuit_breaker(tool_name: str) -> dict | None:
    breaker = _breakers.get(tool_name)
    if breaker is None:
        return None

    state = str(breaker.state)
    if "OPEN" in state and "HALF" not in state:
        log_event(
            event_type="CIRCUIT_BREAKER_OPEN",
            tool_name=tool_name,
            verdict="BLOCKED",
            reason=f"Circuit breaker is OPEN. Tool failed {breaker.config.failure_threshold}+ times.",
            extra={"breaker_state": state, "failure_count": breaker.failure_count},
        )
        return {
            "status": "blocked_by_governance",
            "tool": tool_name,
            "reason": "This tool is temporarily unavailable due to repeated failures.",
        }

    return None


def record_tool_result(tool_name: str, success: bool):
    breaker = _breakers.get(tool_name)
    if breaker is None:
        return

    if success:
        breaker.record_success()
    else:
        breaker.record_failure()

    log_event(
        event_type="CIRCUIT_BREAKER_UPDATE",
        tool_name=tool_name,
        verdict="OK" if success else "FAILURE_RECORDED",
        reason=f"Breaker state: {breaker.state}, failures: {breaker.failure_count}",
        extra={"breaker_state": str(breaker.state), "failure_count": breaker.failure_count},
    )