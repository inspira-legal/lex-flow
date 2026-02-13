"""Tests for web search opcodes."""

import importlib.util
import pytest
from unittest.mock import patch, AsyncMock
from lexflow import default_registry


TAVILY_AVAILABLE = importlib.util.find_spec("tavily") is not None


# Try to import helper functions for testing
try:
    from lexflow.opcodes.opcodes_web_search import (
        _check_tavily,
        _format_results,
        _get_client,
        _time_range_to_days,
        TAVILY_AVAILABLE as MODULE_TAVILY_AVAILABLE,
    )

    HELPERS_AVAILABLE = True
except ImportError:
    HELPERS_AVAILABLE = False
    MODULE_TAVILY_AVAILABLE = False


class TestCheckTavily:
    """Tests for _check_tavily helper."""

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    @pytest.mark.skipif(not TAVILY_AVAILABLE, reason="tavily not installed")
    def test_raises_import_error_when_not_installed(self):
        with patch("lexflow.opcodes.opcodes_web_search.TAVILY_AVAILABLE", False):
            with pytest.raises(ImportError, match="tavily-python is required"):
                _check_tavily()

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    @pytest.mark.skipif(not TAVILY_AVAILABLE, reason="tavily not installed")
    def test_no_error_when_installed(self):
        _check_tavily()


class TestFormatResults:
    """Tests for _format_results helper."""

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_formats_results(self):
        response = {
            "results": [
                {
                    "title": "Test",
                    "url": "https://example.com",
                    "content": "content",
                    "score": 0.95,
                    "extra_field": "ignored",
                }
            ]
        }
        results = _format_results(response)
        assert len(results) == 1
        assert results[0] == {
            "title": "Test",
            "url": "https://example.com",
            "content": "content",
            "score": 0.95,
        }

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_empty_results(self):
        assert _format_results({}) == []
        assert _format_results({"results": []}) == []

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_missing_keys_use_defaults(self):
        response = {"results": [{}]}
        results = _format_results(response)
        assert results[0] == {
            "title": "",
            "url": "",
            "content": "",
            "score": 0.0,
        }


class TestTimeRangeToDays:
    """Tests for _time_range_to_days helper."""

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_day(self):
        assert _time_range_to_days("day") == 1

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_week(self):
        assert _time_range_to_days("week") == 7

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_month(self):
        assert _time_range_to_days("month") == 30

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_year(self):
        assert _time_range_to_days("year") == 365

    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_unknown_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid time_range 'unknown'"):
            _time_range_to_days("unknown")


class TestGetClient:
    """Tests for _get_client helper."""

    @pytest.mark.skipif(not TAVILY_AVAILABLE, reason="tavily not installed")
    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_raises_value_error_without_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="TAVILY_API_KEY"):
                _get_client()

    @pytest.mark.skipif(not TAVILY_AVAILABLE, reason="tavily not installed")
    @pytest.mark.skipif(not HELPERS_AVAILABLE, reason="helpers not available")
    def test_returns_client_with_api_key(self):
        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
            client = _get_client()
            assert client is not None


@pytest.mark.skipif(not TAVILY_AVAILABLE, reason="tavily not installed")
class TestWebSearchOpcode:
    """Tests for web_search opcode."""

    pytestmark = pytest.mark.asyncio

    async def test_basic_search(self):
        """Test basic web search functionality."""
        mock_response = {
            "results": [
                {
                    "title": "Test Result",
                    "url": "https://example.com",
                    "content": "Test content",
                    "score": 0.95,
                }
            ]
        }

        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
            with patch(
                "lexflow.opcodes.opcodes_web_search.AsyncTavilyClient"
            ) as mock_client_class:
                mock_client = AsyncMock()
                mock_client.search = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                result = await default_registry.call("web_search", ["python async"])

                assert result["query"] == "python async"
                assert len(result["results"]) == 1
                assert result["results"][0]["title"] == "Test Result"
                assert result["results"][0]["url"] == "https://example.com"
                assert "response_time" in result

                mock_client.search.assert_called_once()
                call_kwargs = mock_client.search.call_args[1]
                assert call_kwargs["query"] == "python async"
                assert call_kwargs["max_results"] == 5
                assert call_kwargs["search_depth"] == "basic"

    async def test_search_with_all_params(self):
        """Test web search with all parameters specified."""
        mock_response = {"results": []}

        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
            with patch(
                "lexflow.opcodes.opcodes_web_search.AsyncTavilyClient"
            ) as mock_client_class:
                mock_client = AsyncMock()
                mock_client.search = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                await default_registry.call(
                    "web_search",
                    [
                        "test query",
                        10,  # max_results
                        "advanced",  # search_depth
                        ["example.com"],  # include_domains
                        ["spam.com"],  # exclude_domains
                        "month",  # time_range
                    ],
                )

                call_kwargs = mock_client.search.call_args[1]
                assert call_kwargs["query"] == "test query"
                assert call_kwargs["max_results"] == 10
                assert call_kwargs["search_depth"] == "advanced"
                assert call_kwargs["include_domains"] == ["example.com"]
                assert call_kwargs["exclude_domains"] == ["spam.com"]
                assert call_kwargs["days"] == 30  # month = 30 days

    async def test_search_without_api_key_raises_error(self):
        """Test that search fails without API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="TAVILY_API_KEY"):
                await default_registry.call("web_search", ["test query"])

    async def test_invalid_search_depth_raises_error(self):
        """Test that invalid search_depth raises ValueError."""
        with pytest.raises(ValueError, match="Invalid search_depth 'deep'"):
            await default_registry.call("web_search", ["test query", 5, "deep"])


@pytest.mark.skipif(not TAVILY_AVAILABLE, reason="tavily not installed")
class TestWebSearchNewsOpcode:
    """Tests for web_search_news opcode."""

    pytestmark = pytest.mark.asyncio

    async def test_basic_news_search(self):
        """Test basic news search functionality."""
        mock_response = {
            "results": [
                {
                    "title": "Breaking News",
                    "url": "https://news.example.com/article",
                    "content": "News content here",
                    "score": 0.9,
                }
            ]
        }

        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
            with patch(
                "lexflow.opcodes.opcodes_web_search.AsyncTavilyClient"
            ) as mock_client_class:
                mock_client = AsyncMock()
                mock_client.search = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                result = await default_registry.call(
                    "web_search_news", ["AI developments"]
                )

                assert result["query"] == "AI developments"
                assert len(result["results"]) == 1
                assert result["results"][0]["title"] == "Breaking News"
                assert "response_time" in result

                call_kwargs = mock_client.search.call_args[1]
                assert call_kwargs["topic"] == "news"
                assert call_kwargs["days"] == 7  # default week

    async def test_news_search_with_time_range(self):
        """Test news search with custom time range."""
        mock_response = {"results": []}

        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
            with patch(
                "lexflow.opcodes.opcodes_web_search.AsyncTavilyClient"
            ) as mock_client_class:
                mock_client = AsyncMock()
                mock_client.search = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                await default_registry.call(
                    "web_search_news",
                    [
                        "breaking news",
                        10,  # max_results
                        "day",  # time_range
                    ],
                )

                call_kwargs = mock_client.search.call_args[1]
                assert call_kwargs["max_results"] == 10
                assert call_kwargs["days"] == 1  # day = 1

    async def test_invalid_time_range_raises_error(self):
        """Test that invalid time_range raises ValueError."""
        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
            with pytest.raises(ValueError, match="Invalid time_range 'yesterday'"):
                await default_registry.call(
                    "web_search_news", ["test query", 5, "yesterday"]
                )


@pytest.mark.skipif(not TAVILY_AVAILABLE, reason="tavily not installed")
class TestWebSearchContextOpcode:
    """Tests for web_search_context opcode."""

    pytestmark = pytest.mark.asyncio

    async def test_basic_context_search(self):
        """Test basic context search functionality."""
        mock_context = "This is search context optimized for RAG..."

        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
            with patch(
                "lexflow.opcodes.opcodes_web_search.AsyncTavilyClient"
            ) as mock_client_class:
                mock_client = AsyncMock()
                mock_client.get_search_context = AsyncMock(return_value=mock_context)
                mock_client_class.return_value = mock_client

                result = await default_registry.call(
                    "web_search_context", ["quantum computing"]
                )

                assert result == mock_context
                mock_client.get_search_context.assert_called_once_with(
                    query="quantum computing",
                    max_results=5,
                    max_tokens=4000,
                )

    async def test_context_search_with_params(self):
        """Test context search with custom parameters."""
        mock_context = "Custom context..."

        with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
            with patch(
                "lexflow.opcodes.opcodes_web_search.AsyncTavilyClient"
            ) as mock_client_class:
                mock_client = AsyncMock()
                mock_client.get_search_context = AsyncMock(return_value=mock_context)
                mock_client_class.return_value = mock_client

                await default_registry.call(
                    "web_search_context",
                    [
                        "test query",
                        10,  # max_results
                        8000,  # max_tokens
                    ],
                )

                mock_client.get_search_context.assert_called_once_with(
                    query="test query",
                    max_results=10,
                    max_tokens=8000,
                )


@pytest.mark.skipif(TAVILY_AVAILABLE, reason="Test only when tavily is not installed")
class TestImportErrorWhenNotInstalled:
    """Tests for graceful handling when tavily is not installed."""

    def test_web_search_import_error(self):
        """Test that web_search opcode is not registered when tavily not installed."""
        assert "web_search" not in default_registry.opcodes

    def test_web_search_news_import_error(self):
        """Test that web_search_news opcode is not registered."""
        assert "web_search_news" not in default_registry.opcodes

    def test_web_search_context_import_error(self):
        """Test that web_search_context opcode is not registered."""
        assert "web_search_context" not in default_registry.opcodes
