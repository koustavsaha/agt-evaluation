"""
Tool: Web Search
Purpose: Lets the agent search the web for information.
Safety: SAFE — read-only, no side effects.
"""

import datetime


def web_search(query: str) -> dict:
    """Search the web for information on a topic.

    Args:
        query: What to search for (e.g., "AI governance frameworks").

    Returns:
        A dictionary containing search results.
    """
    # This is a simulation. In production, you would call a real search API.
    print(f"    [TOOL EXECUTING] web_search(query='{query}')")

    return {
        "status": "success",
        "query": query,
        "results": [
            {
                "title": f"Research paper about: {query}",
                "url": f"https://example.com/paper/{query.replace(' ', '-')}",
                "snippet": f"This is a simulated search result for '{query}'.",
            }
        ],
        "timestamp": datetime.datetime.now().isoformat(),
    }