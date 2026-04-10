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
    """Write an audit event to all log destinations.
    Trust score and tier are ALWAYS included automatically."""

    event = {
        "event_type": event_type,
        "tool_name": tool_name,
        "verdict": verdict,
        "reason": reason,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    if extra:
        event.update(extra)

    # Always include trust score (import here to avoid circular imports)
    try:
        from research_agent.governance.identity import get_trust_score, get_trust_tier
        event["trust_score"] = get_trust_score()
        event["trust_tier"] = get_trust_tier()
    except Exception:
        pass  # Identity not initialized yet during startup

    # 1. Write to local file
    with open(LOCAL_LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

    # 2. Print to console — always shows trust
    trust_info = f"trust={event.get('trust_score', '?')}/{event.get('trust_tier', '?')}"
    msg = (
        f"{event_type:25s} | tool={tool_name:20s} | "
        f"verdict={verdict:8s} | {trust_info:25s} | {reason}"
    )
    logger.info(msg)

    # 3. Send structured JSON to Cloud Logging (if available)
    if _cloud_logger is not None:
        try:
            _cloud_logger.log_struct(
                event,
                severity="WARNING" if verdict in ("DENIED", "BLOCKED") else "INFO",
            )
        except Exception as e:
            logger.warning(f"Cloud Logging write failed: {e}")

    return event