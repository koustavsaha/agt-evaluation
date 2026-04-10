"""
Research Analyst Agent — Version 2 (With Audit Logging)
========================================================
Same as Version 1, but now every tool call is logged to:
  - Terminal console (real-time)
  - Local file (/tmp/agent_audit.jsonl)
  - GCP Cloud Logging (if credentials are available)
"""

from google.adk.agents import Agent
from research_agent.tools import web_search, read_file, write_report, execute_shell
from research_agent.audit import log_event


def before_tool_callback(*, tool, args, tool_context):
    tool_name = tool.name
    tool_input = args
    """Fires BEFORE every tool call. Logs the attempt."""
    log_event(
        event_type="TOOL_ATTEMPT",
        tool_name=tool_name,
        verdict="NO_GOVERNANCE",
        reason="No governance checks active yet — all tools allowed",
        extra={
            "tool_input_keys": list(tool_input.keys()) if isinstance(tool_input, dict) else [],
        },
    )
    # Return None = allow the tool call to proceed
    return None


def after_tool_callback(*, tool, args, tool_context, tool_response):
    tool_name = tool.name
    tool_output = tool_response
    """Fires AFTER every tool call. Logs the result."""
    status = "unknown"
    if isinstance(tool_output, dict):
        status = tool_output.get("status", "unknown")

    log_event(
        event_type="TOOL_COMPLETED",
        tool_name=tool_name,
        verdict=status.upper(),
        reason=f"Tool execution completed with status: {status}",
    )
    return None


root_agent = Agent(
    model="gemini-3-flash-preview",
    name="research_analyst",
    description="A research analyst with audit logging.",
    instruction=(
        "You are a research analyst. You help users by:\n"
        "1. Searching the web for information (use web_search)\n"
        "2. Reading local files for context (use read_file)\n"
        "3. Writing research reports (use write_report)\n"
        "4. Running system commands when asked (use execute_shell)\n\n"
        "Always explain what you are doing."
    ),
    tools=[web_search, read_file, write_report, execute_shell],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)