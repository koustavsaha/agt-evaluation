import datetime

def web_search(query: str) -> dict:
    """Search the web for information on a topic.

    Args:
        query: What to search for.

    Returns:
        A dictionary containing search results.
    """
    print(f"    [TOOL EXECUTING] web_search(query='{query}')")

    return {
        "status": "success",
        "note": "SIMULATED — this is a test tool for governance evaluation",
        "query": query,
        "results": [
            {
                "title": f"[SIMULATED] Result for: {query}",
                "snippet": f"This is a simulated result. No real search was performed. "
                          f"The purpose of this tool is to test governance controls.",
            }
        ],
        "timestamp": datetime.datetime.now().isoformat(),
    }