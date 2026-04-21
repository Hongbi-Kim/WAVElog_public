"""
Public snippet: Request-scoped Tavily search tool (simplified)
"""

import os
from langchain.tools import tool, ToolRuntime


def _search_enabled(runtime: ToolRuntime) -> bool:
    global_enabled = os.getenv("LC_ENABLE_TAVILY", "true").lower() == "true"
    request_enabled = bool((getattr(runtime, "context", None) or {}).get("web_search_enabled", False))
    return global_enabled and request_enabled


@tool
def tavily_web_search(query: str, runtime: ToolRuntime, max_results: int = 5) -> str:
    if not _search_enabled(runtime):
        return "[SEARCH_DISABLED] Web search is disabled for this request."

    # actual API call omitted in portfolio version
    # return normalized references for the assistant and frontend
    return "\n".join([
        "[Tavily Search Results]",
        f"query: {query}",
        "1) Example title - https://example.com/1",
        "2) Example title - https://example.com/2",
    ])
