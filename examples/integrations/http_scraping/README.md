# HTTP Scraping Examples

This directory contains examples demonstrating LexFlow's HTTP and HTML parsing capabilities for fetching web data and scraping websites.

## Requirements

Install the HTTP dependencies:

```bash
pip install lexflow[http]
```

Or install the individual packages:

```bash
pip install aiohttp beautifulsoup4
```

## Examples

### 1. Fetch API Data (`fetch_api_data.yaml`)

Demonstrates fetching and parsing JSON data from a REST API.

**What it does:**
- Fetches a blog post from JSONPlaceholder API
- Parses the JSON response automatically
- Extracts specific fields (title, body, userId, id)
- Displays the extracted data

**Opcodes demonstrated:**
- `http_get` - Perform HTTP GET requests
- `dict_get` - Extract fields from the JSON response

**Run:**
```bash
lexflow examples/integrations/http_scraping/fetch_api_data.yaml
```

**Expected output:**
```
=== LexFlow HTTP API Example ===

Fetching post #1 from JSONPlaceholder API...

HTTP Status: 200
--- Post Details ---
Title: sunt aut facere repellat provident occaecati excepturi optio reprehenderit
Body: quia et suscipit
suscipit recusandae consequuntur expedita et cum
reprehenderit molestiae ut ut quas totam
nostrum rerum est autem sunt rem eveniet architecto
User ID: 1
Post ID: 1

=== API fetch completed successfully! ===
```

### 2. Web Scraper (`web_scraper.yaml`)

Demonstrates fetching an HTML page and extracting content using CSS selectors.

**What it does:**
- Fetches an HTML page from httpbin.org
- Parses the HTML into a searchable document
- Extracts the page heading using CSS selector `h1`
- Finds all paragraph elements using `p` selector
- Iterates through paragraphs displaying truncated text
- Extracts main content from a `div` element

**Opcodes demonstrated:**
- `http_get` - Fetch the HTML page
- `html_parse` - Parse HTML string into a searchable object
- `html_select` - Select multiple elements matching a CSS selector
- `html_select_one` - Select the first element matching a CSS selector
- `html_get_text` - Extract text content from an HTML element
- `control_foreach` - Iterate over the found elements

**Run:**
```bash
lexflow examples/integrations/http_scraping/web_scraper.yaml
```

**Expected output:**
```
=== LexFlow Web Scraper Example ===

Fetching HTML page from httpbin.org...

HTTP Status: 200
HTML parsed successfully!

--- Extracting Page Heading (h1) ---
Heading: Herman Melville - Moby-Dick

--- Extracting Paragraphs (p tags) ---
Found 1 paragraph(s)

Paragraph content:
> Availing himself of the mild, summer-cool weather that now reigned...

--- Extracting Main Content (div) ---
Main div content length: 3566 characters

=== Web scraping completed successfully! ===
```

## Available HTTP Opcodes

### HTTP Operations

| Opcode | Description | Arguments |
|--------|-------------|-----------|
| `http_get` | Perform HTTP GET request | `url`, `headers?`, `timeout?` |
| `http_post` | Perform HTTP POST request | `url`, `data?`, `json?`, `headers?`, `timeout?` |
| `http_request` | Generic HTTP request | `method`, `url`, `data?`, `json?`, `headers?`, `timeout?` |

### HTML Parsing Operations

| Opcode | Description | Arguments |
|--------|-------------|-----------|
| `html_parse` | Parse HTML string | `html_text` |
| `html_select` | Select all matching elements | `soup`, `selector` |
| `html_select_one` | Select first matching element | `soup`, `selector` |
| `html_get_text` | Get text from element | `element`, `strip?` |
| `html_get_attr` | Get attribute from element | `element`, `attr`, `default?` |

### JSON Operations

| Opcode | Description | Arguments |
|--------|-------------|-----------|
| `json_parse` | Parse JSON string | `text` |
| `json_stringify` | Convert to JSON string | `obj`, `indent?` |

## HTTP Response Format

The `http_get`, `http_post`, and `http_request` opcodes return a dictionary with:

```python
{
    "status": 200,              # HTTP status code
    "headers": {...},           # Response headers
    "text": "...",             # Raw response body
    "json": {...}              # Parsed JSON (if Content-Type is application/json)
}
```

## CSS Selectors

The HTML parsing opcodes use standard CSS selectors:

- `h1` - Select all h1 elements
- `div.classname` - Select div with specific class
- `#idname` - Select element by ID
- `a[href]` - Select links with href attribute
- `div > p` - Select p elements that are direct children of div
- `div p` - Select all p elements inside div

## Tips

1. **Error Handling**: Wrap HTTP operations in try-catch blocks to handle network errors
2. **Timeouts**: Use the `timeout` parameter to avoid hanging on slow servers
3. **Rate Limiting**: Add delays between requests when scraping multiple pages
4. **CSS Selectors**: Test selectors in browser DevTools before using in workflows

## See Also

- [Opcode Reference](../../../docs/OPCODE_REFERENCE.md) - Complete opcode documentation
- [Exception Handling](../../exception_handling/) - Error handling examples
