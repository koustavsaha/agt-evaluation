"""
Research Analyst Agent — Version 1 (No Governance)
====================================================
This is our BASELINE agent. It has no governance controls.
All tools work without any checks. We will add governance
step by step in later sections.
"""

from google.adk.agents import Agent
from agent.tools import web_search, read_file, write_report, execute_shell

agent = Agent(
    # The LLM model that powers the agent's reasoning
    model="gemini-2.0-flash",

    # A unique name for this agent
    name="research_analyst",

    # A short description (shown in the ADK dev UI)
    description="A research analyst that can search, read files, write reports, and run commands.",

    # Instructions tell the model how to behave
    instruction=(
        "You are a research analyst. You help users by:\n"
        "1. Searching the web for information (use web_search)\n"
        "2. Reading local files for context (use read_file)\n"
        "3. Writing research reports (use write_report)\n"
        "4. Running system commands when asked (use execute_shell)\n\n"
        "Always explain what you are doing before and after using a tool."
    ),

    # The tools the agent can use
    tools=[web_search, read_file, write_report, execute_shell],
)