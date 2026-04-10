"""
Audit Logger — writes every agent action to:
  1. A local JSONL file (/tmp/agent_audit.jsonl) — always works
  2. GCP Cloud Logging — works when running on GCP or with credentials
  3. Console print — for real-time visibility in your terminal
"""

import datetime
import json
import logging
import os

# ── Local file log ──
LOCAL_LOG_FILE = "/tmp/agent_audit.jsonl"

# ── Standard Python logger (for console output) ──
logger = logging.getLogger("agent-audit")
logger.setLevel(logging.INFO)

# Console handler (prints to your terminal)
if not logger.handlers:  # Avoid adding duplicate handlers on reload
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("  [AUDIT] %(message)s"))
    logger.addHandler(console_handler)

# ── Try to set up GCP Cloud Logging ──
_cloud_logger = None
try:
    import google.cloud.logging as cloud_logging

    # This will use Application Default Credentials
    # On GCP: works automatically
    # On Mac: works if you ran 'gcloud auth application-default login'
    client = cloud_logging.Client()

    # Get a dedicated Cloud Logging logger (NOT setup_logging which
    # hijacks the root logger — we want explicit control)
    _cloud_logger = client.logger("agent-governance-audit")

    logger.info("Cloud Logging: ENABLED (logs visible in GCP Console)")
except Exception as e:
    logger.info(f"Cloud Logging: DISABLED ({e}). Using local file only.")


def log_event(
    event_type: str,
    tool_name: str = "",
    verdict: str = "",
    reason: str = "",
    extra: dict = None,
):
    """
    Write an audit event to all log destinations.

    Args:
        event_type: What happened (e.g., "TOOL_ATTEMPT", "POLICY_DENIED")
        tool_name: Which tool was involved
        verdict: The governance decision (e.g., "ALLOWED", "DENIED")
        reason: Why this decision was made
        extra: Any additional data to include
    """
    event = {
        "event_type": event_type,
        "tool_name": tool_name,
        "verdict": verdict,
        "reason": reason,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    if extra:
        event.update(extra)

    # 1. Write to local file
    with open(LOCAL_LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

    # 2. Print to console
    msg = f"{event_type:25s} | tool={tool_name:20s} | verdict={verdict:8s} | {reason}"
    logger.info(msg)

    # 3. Send structured JSON to Cloud Logging (if available)
    # This creates a log entry with the full event as a JSON payload,
    # which you can filter in GCP Console using jsonPayload.event_type, etc.
    if _cloud_logger is not None:
        try:
            _cloud_logger.log_struct(
                event,
                severity="WARNING" if verdict in ("DENIED", "BLOCKED") else "INFO",
            )
        except Exception as e:
            logger.warning(f"Cloud Logging write failed: {e}")

    return event