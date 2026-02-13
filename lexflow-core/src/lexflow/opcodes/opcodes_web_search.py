"""Web search opcodes using Tavily API.

This module provides opcodes for web search functionality optimized for AI/RAG workflows,
enabling agents to explore and gather information from the internet.

Installation:
    pip install lexflow[search]
    or:
    pip install tavily-python

Environment:
    Set TAVILY_API_KEY environment variable with your Tavily API key.
    Get your key at https://tavily.com
"""

import os
import time
from typing import Any, Dict, List, Optional

from .opcodes import opcode, register_category

try:
    from tavily import AsyncTavilyClient

    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


def _check_tavily():
    """Check if tavily-python is available."""
    if not TAVILY_AVAILABLE:
        raise ImportError(
            "tavily-python is required. Install with: uv add 'lexflow[search]'"
        )


def _get_client() -> "AsyncTavilyClient":
    """Get a configured Tavily client.

    Returns:
        AsyncTavilyClient instance

    Raises:
        ImportError: If tavily-python is not installed
        ValueError: If TAVILY_API_KEY environment variable is not set
    """
    _check_tavily()
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY environment variable not set. "
            "Get your key at https://tavily.com"
        )
    return AsyncTavilyClient(api_key=api_key)


def _format_results(response: dict) -> list:
    """Extract and normalize results from a Tavily API response."""
    return [
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", ""),
            "score": item.get("score", 0.0),
        }
        for item in response.get("results", [])
    ]


def register_web_search_opcodes():
    """Register web search opcodes to the default registry."""
    if not TAVILY_AVAILABLE:
        return

    register_category(
        id="web_search",
        label="Web Search",
        prefix="web_search",
        color="#8B5CF6",
        icon="🔍",
        requires="search",
        order=215,
    )

    @opcode(category="web_search")
    async def web_search(
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        time_range: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform a general web search using Tavily API.

        Args:
            query: The search query string
            max_results: Maximum number of results to return (default: 5)
            search_depth: Search depth - "basic" for fast results, "advanced" for
                         more comprehensive results (default: "basic")
            include_domains: List of domains to include in search (optional)
            exclude_domains: List of domains to exclude from search (optional)
            time_range: Time range filter - "day", "week", "month", or "year" (optional)

        Returns:
            Dict with keys:
            - query: The original query string
            - results: List of result dicts, each with:
                - title: Page title
                - url: Page URL
                - content: Snippet/content from the page
                - score: Relevance score (0-1)
            - response_time: Time taken for the search in seconds

        Example:
            query: "Python 3.12 new features"
            max_results: 5
            search_depth: "basic"
        """
        if search_depth not in ("basic", "advanced"):
            raise ValueError(
                f"Invalid search_depth '{search_depth}'. Must be 'basic' or 'advanced'"
            )

        client = _get_client()
        start_time = time.monotonic()

        # Build search kwargs
        kwargs: Dict[str, Any] = {
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
        }

        if include_domains:
            kwargs["include_domains"] = include_domains
        if exclude_domains:
            kwargs["exclude_domains"] = exclude_domains
        if time_range:
            kwargs["days"] = _time_range_to_days(time_range)

        response = await client.search(**kwargs)
        response_time = time.monotonic() - start_time

        return {
            "query": query,
            "results": _format_results(response),
            "response_time": response_time,
        }

    @opcode(category="web_search")
    async def web_search_news(
        query: str,
        max_results: int = 5,
        time_range: str = "week",
    ) -> Dict[str, Any]:
        """Search for news articles using Tavily API.

        This is a specialized search focused on news content with a default
        time range of one week for recent news.

        Args:
            query: The search query string
            max_results: Maximum number of results to return (default: 5)
            time_range: Time range filter - "day", "week", "month", or "year"
                       (default: "week")

        Returns:
            Dict with keys:
            - query: The original query string
            - results: List of result dicts, each with:
                - title: Article title
                - url: Article URL
                - content: Snippet/content from the article
                - score: Relevance score (0-1)
            - response_time: Time taken for the search in seconds

        Example:
            query: "artificial intelligence breakthroughs"
            max_results: 5
            time_range: "week"
        """
        days = _time_range_to_days(time_range)
        client = _get_client()
        start_time = time.monotonic()

        response = await client.search(
            query=query,
            max_results=max_results,
            topic="news",
            days=days,
        )
        response_time = time.monotonic() - start_time

        return {
            "query": query,
            "results": _format_results(response),
            "response_time": response_time,
        }

    @opcode(category="web_search")
    async def web_search_context(
        query: str,
        max_results: int = 5,
        max_tokens: int = 4000,
    ) -> str:
        """Search the web and return context optimized for RAG/agent prompts.

        This opcode returns a plain string (not a dict) of search results ready
        to be injected directly into LLM prompts. It uses Tavily's
        get_search_context() method which is optimized for RAG workflows.

        Args:
            query: The search query string
            max_results: Maximum number of results to include (default: 5)
            max_tokens: Maximum tokens in the returned context (default: 4000)

        Returns:
            A formatted string containing search results optimized for use
            as context in LLM prompts.

        Example:
            query: "quantum computing applications 2024"
            max_results: 5
            max_tokens: 4000
        """
        client = _get_client()

        context = await client.get_search_context(
            query=query,
            max_results=max_results,
            max_tokens=max_tokens,
        )

        return context


def _time_range_to_days(time_range: str) -> int:
    """Convert time range string to number of days.

    Args:
        time_range: One of "day", "week", "month", or "year"

    Returns:
        Number of days corresponding to the time range

    Raises:
        ValueError: If time_range is not a valid option
    """
    mapping = {
        "day": 1,
        "week": 7,
        "month": 30,
        "year": 365,
    }
    if time_range not in mapping:
        raise ValueError(
            f"Invalid time_range '{time_range}'. Must be one of: day, week, month, year"
        )
    return mapping[time_range]
