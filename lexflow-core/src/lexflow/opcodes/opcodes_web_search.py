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

try:
    from tavily import AsyncTavilyClient

    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


def _check_tavily():
    """Check if tavily-python is available and raise helpful error if not."""
    if not TAVILY_AVAILABLE:
        raise ImportError(
            "tavily-python is not installed. Install it with:\n"
            "  pip install lexflow[search]\n"
            "or:\n"
            "  pip install tavily-python"
        )


def _get_client() -> "AsyncTavilyClient":
    """Get a configured Tavily client.

    Returns:
        AsyncTavilyClient instance

    Raises:
        ValueError: If TAVILY_API_KEY environment variable is not set
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY environment variable not set. "
            "Get your key at https://tavily.com"
        )
    return AsyncTavilyClient(api_key=api_key)


def register_web_search_opcodes():
    """Register web search opcodes to the default registry."""
    if not TAVILY_AVAILABLE:
        return

    from .opcodes import default_registry

    @default_registry.register()
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
        _check_tavily()

        client = _get_client()
        start_time = time.time()

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
        response_time = time.time() - start_time

        # Format results
        results = []
        for item in response.get("results", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "score": item.get("score", 0.0),
                }
            )

        return {
            "query": query,
            "results": results,
            "response_time": response_time,
        }

    @default_registry.register()
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
        _check_tavily()

        client = _get_client()
        start_time = time.time()

        response = await client.search(
            query=query,
            max_results=max_results,
            topic="news",
            days=_time_range_to_days(time_range),
        )
        response_time = time.time() - start_time

        # Format results
        results = []
        for item in response.get("results", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "score": item.get("score", 0.0),
                }
            )

        return {
            "query": query,
            "results": results,
            "response_time": response_time,
        }

    @default_registry.register()
    async def web_search_context(
        query: str,
        max_results: int = 5,
        max_tokens: int = 4000,
    ) -> str:
        """Search the web and return context optimized for RAG/agent prompts.

        This opcode returns a formatted string of search results ready to be
        used as context in LLM prompts. It uses Tavily's get_search_context()
        method which is optimized for RAG workflows.

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
        _check_tavily()

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
    """
    mapping = {
        "day": 1,
        "week": 7,
        "month": 30,
        "year": 365,
    }
    return mapping.get(time_range, 7)  # Default to week if unknown
