"""HTTP and HTML parsing opcodes for LexFlow.

This module provides opcodes for making HTTP requests and parsing HTML content,
enabling web scraping and API integration workflows.

Installation:
    pip install lexflow[http]
    or:
    pip install aiohttp beautifulsoup4
"""

import json as json_module
from typing import Any, Dict, List, Optional

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


def _check_aiohttp():
    """Check if aiohttp is available and raise helpful error if not."""
    if not AIOHTTP_AVAILABLE:
        raise ImportError(
            "aiohttp is not installed. Install it with:\n"
            "  pip install lexflow[http]\n"
            "or:\n"
            "  pip install aiohttp"
        )


def _check_bs4():
    """Check if beautifulsoup4 is available and raise helpful error if not."""
    if not BS4_AVAILABLE:
        raise ImportError(
            "beautifulsoup4 is not installed. Install it with:\n"
            "  pip install lexflow[http]\n"
            "or:\n"
            "  pip install beautifulsoup4"
        )


def register_http_opcodes():
    """Register HTTP and HTML parsing opcodes to the default registry."""
    if not AIOHTTP_AVAILABLE and not BS4_AVAILABLE:
        return

    from .opcodes import default_registry

    # ============================================================================
    # HTTP Operations (require aiohttp)
    # ============================================================================

    if AIOHTTP_AVAILABLE:

        @default_registry.register()
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
                Response dict with keys:
                - status: HTTP status code (int)
                - headers: Response headers (dict)
                - text: Response body as text (str)
                - json: Parsed JSON if content-type is application/json (dict or None)

            Example:
                url: "https://api.example.com/data"
                headers: {"Authorization": "Bearer token123"}
            """
            _check_aiohttp()

            client_timeout = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.get(url, headers=headers) as response:
                    text = await response.text()

                    # Try to parse JSON if content-type suggests it
                    json_data = None
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
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

        @default_registry.register()
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
                json: JSON data to send (for JSON POST, sets Content-Type automatically)
                headers: Optional dictionary of HTTP headers
                timeout: Request timeout in seconds (default: 30.0)

            Returns:
                Response dict with keys:
                - status: HTTP status code (int)
                - headers: Response headers (dict)
                - text: Response body as text (str)
                - json: Parsed JSON if content-type is application/json (dict or None)

            Example:
                url: "https://api.example.com/users"
                json: {"name": "Alice", "email": "alice@example.com"}

            Note:
                If both data and json are provided, json takes precedence.
            """
            _check_aiohttp()

            client_timeout = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.post(
                    url, data=data, json=json, headers=headers
                ) as response:
                    text = await response.text()

                    # Try to parse JSON if content-type suggests it
                    json_data = None
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
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

        @default_registry.register()
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
                Response dict with keys:
                - status: HTTP status code (int)
                - headers: Response headers (dict)
                - text: Response body as text (str)
                - json: Parsed JSON if content-type is application/json (dict or None)

            Example:
                method: "PUT"
                url: "https://api.example.com/users/123"
                json: {"name": "Updated Name"}
            """
            _check_aiohttp()

            method = method.upper()
            client_timeout = aiohttp.ClientTimeout(total=timeout)
            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.request(
                    method, url, data=data, json=json, headers=headers
                ) as response:
                    text = await response.text()

                    # Try to parse JSON if content-type suggests it
                    json_data = None
                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" in content_type:
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

    # ============================================================================
    # HTML Parsing Operations (require beautifulsoup4)
    # ============================================================================

    if BS4_AVAILABLE:

        @default_registry.register()
        async def html_parse(html_text: str) -> Any:
            """Parse an HTML string into a BeautifulSoup object.

            Args:
                html_text: HTML content as a string

            Returns:
                BeautifulSoup object that can be used with html_select* opcodes

            Example:
                html_text: "<html><body><h1>Hello</h1></body></html>"
            """
            _check_bs4()
            return BeautifulSoup(html_text, "html.parser")

        @default_registry.register()
        async def html_select(soup: Any, selector: str) -> List[Any]:
            """Select elements matching a CSS selector.

            Args:
                soup: BeautifulSoup object or element (from html_parse)
                selector: CSS selector string

            Returns:
                List of matching elements (may be empty)

            Example:
                soup: { node: parsed_html }
                selector: "div.item > a.link"
            """
            _check_bs4()
            return soup.select(selector)

        @default_registry.register()
        async def html_select_one(soup: Any, selector: str) -> Optional[Any]:
            """Select the first element matching a CSS selector.

            Args:
                soup: BeautifulSoup object or element (from html_parse)
                selector: CSS selector string

            Returns:
                First matching element, or None if no match found

            Example:
                soup: { node: parsed_html }
                selector: "h1.title"
            """
            _check_bs4()
            return soup.select_one(selector)

        @default_registry.register()
        async def html_get_text(element: Any, strip: bool = True) -> str:
            """Get the text content from an HTML element.

            Args:
                element: BeautifulSoup element
                strip: Whether to strip leading/trailing whitespace (default: True)

            Returns:
                Text content of the element

            Example:
                element: { node: title_element }
                strip: true
            """
            _check_bs4()
            if element is None:
                return ""

            text = element.get_text()
            if strip:
                text = text.strip()
            return text

        @default_registry.register()
        async def html_get_attr(
            element: Any, attr: str, default: Optional[str] = None
        ) -> Optional[str]:
            """Get an attribute value from an HTML element.

            Args:
                element: BeautifulSoup element
                attr: Attribute name (e.g., "href", "class", "id", "src")
                default: Value to return if attribute not found (default: None)

            Returns:
                Attribute value as string, or default if not found

            Example:
                element: { node: link_element }
                attr: "href"
                default: "#"

            Note:
                For attributes that can have multiple values (like "class"),
                returns them joined with spaces.
            """
            _check_bs4()
            if element is None:
                return default

            value = element.get(attr, default)
            # Handle list attributes (like class)
            if isinstance(value, list):
                return " ".join(value)
            return value

    # ============================================================================
    # JSON Operations (no external dependencies)
    # ============================================================================

    @default_registry.register()
    async def json_parse(text: str) -> Any:
        """Parse a JSON string into a Python object.

        Args:
            text: JSON string to parse

        Returns:
            Parsed Python object (dict, list, str, int, float, bool, or None)

        Raises:
            ValueError: If the string is not valid JSON

        Example:
            text: '{"name": "Alice", "age": 30}'
        """
        try:
            return json_module.loads(text)
        except json_module.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    @default_registry.register()
    async def json_stringify(obj: Any, indent: Optional[int] = None) -> str:
        """Convert a Python object to a JSON string.

        Args:
            obj: Python object to serialize (dict, list, str, int, float, bool, None)
            indent: Number of spaces for indentation (None for compact output)

        Returns:
            JSON string representation

        Raises:
            TypeError: If the object is not JSON serializable

        Example:
            obj: {"name": "Alice", "items": [1, 2, 3]}
            indent: 2
        """
        try:
            return json_module.dumps(obj, indent=indent)
        except (TypeError, ValueError) as e:
            raise TypeError(f"Object is not JSON serializable: {e}")
