"""HTTP and HTML parsing opcodes for LexFlow.

This module provides opcodes for making HTTP requests and parsing HTML content,
enabling web scraping and API integration workflows.

Installation:
    pip install lexflow[http]
"""

import json as json_module
from typing import Any, AsyncGenerator, Dict, List, Optional

from .opcodes import opcode, register_category

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


def register_http_opcodes():
    """Register HTTP and HTML parsing opcodes to the default registry."""
    if not AIOHTTP_AVAILABLE and not BS4_AVAILABLE:
        return

    register_category(
        id="http",
        label="HTTP Operations",
        prefix="http_",
        color="#3B82F6",
        icon="🌐",
        requires="http",
        order=210,
    )

    register_category(
        id="html",
        label="HTML Operations",
        prefix="html_",
        color="#E34F26",
        icon="📄",
        requires="http",
        order=211,
    )

    register_category(
        id="json",
        label="JSON Operations",
        prefix="json_",
        color="#F59E0B",
        icon="📋",
        order=212,
    )

    # =========================================================================
    # HTTP Operations (require aiohttp)
    # =========================================================================

    if AIOHTTP_AVAILABLE:

        @opcode(category="http")
        async def http_get(
            url: str,
            headers: Optional[Dict[str, str]] = None,
            timeout: float = 30.0,
        ) -> Dict[str, Any]:
            """Perform an HTTP GET request.

            Args:
                url: The URL to request
                headers: Optional dictionary of HTTP headers
                timeout: Request timeout in seconds (default: 30.0)

            Returns:
                Response dict with keys: status, headers, text, json
            """
            client_timeout = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.get(url, headers=headers) as response:
                    text = await response.text()
                    json_data = None
                    if "application/json" in response.headers.get("Content-Type", ""):
                        try:
                            json_data = json_module.loads(text)
                        except json_module.JSONDecodeError:
                            pass

                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "text": text,
                        "json": json_data,
                    }

        @opcode(category="http")
        async def http_post(
            url: str,
            data: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: float = 30.0,
        ) -> Dict[str, Any]:
            """Perform an HTTP POST request.

            Args:
                url: The URL to request
                data: Form data to send (for form-encoded POST)
                json: JSON data to send (sets Content-Type automatically)
                headers: Optional dictionary of HTTP headers
                timeout: Request timeout in seconds (default: 30.0)

            Returns:
                Response dict with keys: status, headers, text, json
            """
            client_timeout = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.post(
                    url, data=data, json=json, headers=headers
                ) as response:
                    text = await response.text()
                    json_data = None
                    if "application/json" in response.headers.get("Content-Type", ""):
                        try:
                            json_data = json_module.loads(text)
                        except json_module.JSONDecodeError:
                            pass

                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "text": text,
                        "json": json_data,
                    }

        @opcode(category="http")
        async def http_request(
            method: str,
            url: str,
            data: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: float = 30.0,
        ) -> Dict[str, Any]:
            """Perform a generic HTTP request with any method.

            Args:
                method: HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
                url: The URL to request
                data: Form data to send
                json: JSON data to send (sets Content-Type automatically)
                headers: Optional dictionary of HTTP headers
                timeout: Request timeout in seconds (default: 30.0)

            Returns:
                Response dict with keys: status, headers, text, json
            """
            method = method.upper()
            client_timeout = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.request(
                    method, url, data=data, json=json, headers=headers
                ) as response:
                    text = await response.text()
                    json_data = None
                    if "application/json" in response.headers.get("Content-Type", ""):
                        try:
                            json_data = json_module.loads(text)
                        except json_module.JSONDecodeError:
                            pass

                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "text": text,
                        "json": json_data,
                    }

        # =====================================================================
        # HTTP Streaming Operations
        # =====================================================================

        @opcode(category="http")
        async def http_stream_lines(
            url: str,
            headers: Optional[Dict[str, str]] = None,
            timeout: float = 30.0,
        ) -> AsyncGenerator[str, None]:
            """Stream lines from an HTTP response.

            Yields each line as it becomes available. Useful for streaming APIs
            like Server-Sent Events or newline-delimited JSON.

            Args:
                url: The URL to request
                headers: Optional dictionary of HTTP headers
                timeout: Request timeout in seconds (default: 30.0)

            Yields:
                Each line from the response (stripped of newlines)
            """
            client_timeout = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.get(url, headers=headers) as response:
                    async for line in response.content:
                        decoded = line.decode("utf-8").strip()
                        if decoded:
                            yield decoded

        @opcode(category="http")
        async def http_stream_chunks(
            url: str,
            chunk_size: int = 8192,
            headers: Optional[Dict[str, str]] = None,
            timeout: float = 30.0,
        ) -> AsyncGenerator[bytes, None]:
            """Stream chunks from an HTTP response.

            Args:
                url: The URL to request
                chunk_size: Size of each chunk in bytes (default: 8192)
                headers: Optional dictionary of HTTP headers
                timeout: Request timeout in seconds (default: 30.0)

            Yields:
                Byte chunks from the response
            """
            client_timeout = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.get(url, headers=headers) as response:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        yield chunk

        # =====================================================================
        # HTTP Session Operations (context manager support)
        # =====================================================================

        class HTTPSession:
            """Reusable HTTP session for multiple requests."""

            def __init__(
                self,
                timeout: float = 30.0,
                headers: Optional[Dict[str, str]] = None,
            ):
                self.timeout = timeout
                self.headers = headers or {}
                self._session: Optional[aiohttp.ClientSession] = None

            async def __aenter__(self):
                client_timeout = aiohttp.ClientTimeout(total=self.timeout)
                self._session = aiohttp.ClientSession(
                    timeout=client_timeout, headers=self.headers
                )
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if self._session:
                    await self._session.close()
                    self._session = None

            async def get(
                self, url: str, headers: Optional[Dict[str, str]] = None
            ) -> Dict:
                """Perform GET request using this session."""
                async with self._session.get(url, headers=headers) as response:
                    text = await response.text()
                    json_data = None
                    if "application/json" in response.headers.get("Content-Type", ""):
                        try:
                            json_data = json_module.loads(text)
                        except json_module.JSONDecodeError:
                            pass
                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "text": text,
                        "json": json_data,
                    }

            async def post(
                self,
                url: str,
                data: Optional[Dict] = None,
                json: Optional[Dict] = None,
                headers: Optional[Dict[str, str]] = None,
            ) -> Dict:
                """Perform POST request using this session."""
                async with self._session.post(
                    url, data=data, json=json, headers=headers
                ) as response:
                    text = await response.text()
                    json_data = None
                    if "application/json" in response.headers.get("Content-Type", ""):
                        try:
                            json_data = json_module.loads(text)
                        except json_module.JSONDecodeError:
                            pass
                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "text": text,
                        "json": json_data,
                    }

        @opcode(category="http")
        async def http_session_create(
            timeout: float = 30.0,
            headers: Optional[Dict[str, str]] = None,
        ) -> HTTPSession:
            """Create an HTTP session for reuse with control_with.

            Args:
                timeout: Default request timeout in seconds
                headers: Default headers for all requests

            Returns:
                HTTPSession object (use with control_with)
            """
            return HTTPSession(timeout=timeout, headers=headers)

        @opcode(category="http")
        async def http_session_get(
            session: HTTPSession,
            url: str,
            headers: Optional[Dict[str, str]] = None,
        ) -> Dict[str, Any]:
            """Perform GET request using a session.

            Args:
                session: HTTPSession from http_session_create
                url: The URL to request
                headers: Optional additional headers

            Returns:
                Response dict (same as http_get)
            """
            return await session.get(url, headers=headers)

        @opcode(category="http")
        async def http_session_post(
            session: HTTPSession,
            url: str,
            data: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
        ) -> Dict[str, Any]:
            """Perform POST request using a session.

            Args:
                session: HTTPSession from http_session_create
                url: The URL to request
                data: Form data to send
                json: JSON data to send
                headers: Optional additional headers

            Returns:
                Response dict (same as http_post)
            """
            return await session.post(url, data=data, json=json, headers=headers)

    # =========================================================================
    # HTML Parsing Operations (require beautifulsoup4)
    # =========================================================================

    if BS4_AVAILABLE:

        @opcode(category="html")
        async def html_parse(html_text: str) -> Any:
            """Parse an HTML string into a BeautifulSoup object.

            Args:
                html_text: HTML content as a string

            Returns:
                BeautifulSoup object for use with html_select* opcodes
            """
            return BeautifulSoup(html_text, "html.parser")

        @opcode(category="html")
        async def html_select(soup: Any, selector: str) -> List[Any]:
            """Select elements matching a CSS selector.

            Args:
                soup: BeautifulSoup object or element (from html_parse)
                selector: CSS selector string

            Returns:
                List of matching elements (may be empty)
            """
            return soup.select(selector)

        @opcode(category="html")
        async def html_select_one(soup: Any, selector: str) -> Optional[Any]:
            """Select the first element matching a CSS selector.

            Args:
                soup: BeautifulSoup object or element (from html_parse)
                selector: CSS selector string

            Returns:
                First matching element, or None if no match
            """
            return soup.select_one(selector)

        @opcode(category="html")
        async def html_get_text(element: Any, strip: bool = True) -> str:
            """Get the text content from an HTML element.

            Args:
                element: BeautifulSoup element
                strip: Whether to strip whitespace (default: True)

            Returns:
                Text content of the element
            """
            if element is None:
                return ""
            text = element.get_text()
            return text.strip() if strip else text

        @opcode(category="html")
        async def html_get_attr(
            element: Any, attr: str, default: Optional[str] = None
        ) -> Optional[str]:
            """Get an attribute value from an HTML element.

            Args:
                element: BeautifulSoup element
                attr: Attribute name (e.g., "href", "class", "id")
                default: Value to return if attribute not found

            Returns:
                Attribute value as string, or default if not found
            """
            if element is None:
                return default
            value = element.get(attr, default)
            if isinstance(value, list):
                return " ".join(value)
            return value

    # =========================================================================
    # JSON Operations (no external dependencies)
    # =========================================================================

    @opcode(category="json")
    async def json_parse(text: str) -> Any:
        """Parse a JSON string into a Python object.

        Args:
            text: JSON string to parse

        Returns:
            Parsed Python object (dict, list, str, int, float, bool, or None)

        Raises:
            ValueError: If the string is not valid JSON
        """
        try:
            return json_module.loads(text)
        except json_module.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    @opcode(category="json")
    async def json_stringify(obj: Any, indent: Optional[int] = None) -> str:
        """Convert a Python object to a JSON string.

        Args:
            obj: Python object to serialize
            indent: Number of spaces for indentation (None for compact)

        Returns:
            JSON string representation

        Raises:
            TypeError: If the object is not JSON serializable
        """
        try:
            return json_module.dumps(obj, indent=indent)
        except (TypeError, ValueError) as e:
            raise TypeError(f"Object is not JSON serializable: {e}")
