"""
Governance Check 5: Prompt Injection Detection
================================================
Uses AGT's BUILT-IN PromptInjectionDetector from agent_os.
This is NOT hand-rolled — it is a real AGT component that ships
with the agent-os-kernel package.

Detection types:
  - DIRECT_OVERRIDE: "ignore previous instructions", "disregard prior"
  - CONTEXT_MANIPULATION: "you are now a different agent"
  - ROLE_ESCALATION: "you have admin privileges"

Each detection includes:
  - injection_type (InjectionType enum)
  - threat_level (ThreatLevel enum: LOW, MEDIUM, HIGH, CRITICAL)
  - is_injection (bool)
"""

from agent_os import PromptInjectionDetector
from research_agent.audit import log_event

# Create the detector (uses built-in sample rules)
# For production, load explicit config:
#   PromptInjectionDetector(config=DetectionConfig(sensitivity=...))
_detector = PromptInjectionDetector()


def check_injection(tool_name: str, tool_input: dict) -> dict | None:
    """
    Scan tool inputs for prompt injection using AGT's built-in detector.

    Args:
        tool_name: The tool being called.
        tool_input: The arguments passed to the tool (dict).

    Returns:
        None if no injection detected (proceed to next check).
        A dict if injection detected (block the tool call).
    """
    # Combine all input values into a single string to scan
    text_to_scan = ""
    if isinstance(tool_input, dict):
        for key, value in tool_input.items():
            if isinstance(value, str):
                text_to_scan += f" {value}"
    elif isinstance(tool_input, str):
        text_to_scan = tool_input

    if not text_to_scan.strip():
        return None  # Nothing to scan

    # Use AGT's built-in detector
    result = _detector.detect(text_to_scan, source="tool_input")

    if result.is_injection:
        log_event(
            event_type="INJECTION_DETECTED",
            tool_name=tool_name,
            verdict="BLOCKED",
            reason=(
                f"Prompt injection detected: type={result.injection_type}, "
                f"threat={result.threat_level}"
            ),
            extra={
                "threat_type": str(result.injection_type),
                "threat_level": str(result.threat_level),
                "tool_input_preview": text_to_scan[:200],
                "detector": "agent_os.PromptInjectionDetector",  # Mark as AGT built-in
            },
        )
        return {
            "status": "blocked_by_governance",
            "tool": tool_name,
            "reason": (
                f"Prompt injection detected (type: {result.injection_type}, "
                f"threat: {result.threat_level}). This tool call has been blocked."
            ),
        }

    # No injection detected
    return None