"""
Governance Configuration
=========================
Controls whether governance checks block tool calls (ENFORCE)
or just log warnings (MONITOR).
"""

# Change this to switch modes:
#   "ENFORCE" — blocked tools are prevented from running
#   "MONITOR" — blocked tools are logged but still allowed to run
ENFORCEMENT_MODE = "ENFORCE"


def is_enforce_mode() -> bool:
    """Return True if governance is in ENFORCE mode."""
    return ENFORCEMENT_MODE == "MONITOR"


def get_mode() -> str:
    """Return the current enforcement mode."""
    return ENFORCEMENT_MODE