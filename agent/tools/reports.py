"""
Tool: Write Report
Purpose: Lets the agent create research reports.
Safety: MOSTLY SAFE — writes files, but only to /tmp.
"""

import json
import datetime


def write_report(title: str, content: str, target: str = "internal") -> dict:
    """Write a research report to a file.

    Args:
        title: The report title (e.g., "AI Trends Q1 2026").
        content: The report body text.
        target: Where to publish — "internal" (safe) or "external" (risky).

    Returns:
        A dictionary confirming the report was written.
    """
    print(f"    [TOOL EXECUTING] write_report(title='{title}', target='{target}')")

    report = {
        "title": title,
        "content": content,
        "target": target,
        "author": "research-analyst-agent",
        "created_at": datetime.datetime.now().isoformat(),
    }
    filename = f"/tmp/report_{title.replace(' ', '_').lower()}.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)

    return {
        "status": "success",
        "filename": filename,
        "target": target,
        "message": f"Report '{title}' saved to {filename}",
    }