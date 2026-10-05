# Python Web Scraper & Automation

A small Python web scraping project demonstrating HTTP scraping, HTML parsing, asynchronous browser automation, pagination, proxy rotation, error handling, and automated testing.

The project uses [Books to Scrape](https://books.toscrape.com/) as the target website.

---

## Overview

This project contains two scraping approaches:

1. **Requests + BeautifulSoup**
   - Fetches HTML pages using HTTP requests.
   - Parses book information using BeautifulSoup.
   - Handles pagination.
   - Retries failed requests.
   - Saves the scraped data as JSON.

2. **Async Playwright**
   - Uses Playwright's asynchronous API.
   - Automates Chromium.
   - Extracts book information from rendered pages.
   - Handles pagination.
   - Supports authorized proxy configuration.
   - Retries scraping with the next configured proxy when a scraping attempt fails.
   - Saves the scraped data as JSON.

The project also includes a pytest test suite covering parsing, proxy rotation, Playwright scraping, pagination, and failure scenarios.

---

## Features

- HTTP scraping with Requests
- HTML parsing with BeautifulSoup
- Asynchronous browser automation with Playwright
- Chromium automation
- Pagination handling
- Book data extraction
- Rating conversion from text to integer
- Relative URL to absolute URL conversion
- Request retry handling
- Playwright timeout handling
- HTTP error handling
- Proxy rotation using round-robin selection
- Environment variable based proxy configuration
- JSON output
- Structured logging
- Pytest automation tests
- Async Playwright testing with pytest-asyncio

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Main programming language |
| Requests | HTTP requests |
| BeautifulSoup | HTML parsing |
| Playwright | Browser automation |
| Chromium | Automated browser |
| Pytest | Testing framework |
| pytest-asyncio | Async test support |
| JSON | Scraped data output |
| Git | Version control |

---

## Project Structure

```text

Web Scraper - Python/
│
├── scraper/
│   ├── __init__.py
│   ├── parser.py
│   ├── scraper.py
│   ├── playwright_scraper.py
│   └── proxy_manager.py
│
├── tests/
│   ├── conftest.py
│   ├── test_parser.py
│   ├── test_playwright_scraper.py
│   ├── test_proxy_manager.py
│   └── test_scraper_failure.py
│
├── output/
│   ├── results.json
│   └── playwright_results.json
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md

```

**Data Extracted**

For each book, the scraper extracts:
- Title
- Price
- Availability
- Rating
- URL

### Running the Requests Scraper

The Requests scraper follows this flow:

```text
Requests
        ↓
HTTP Response
        ↓
BeautifulSoup
        ↓
HTML Parsing
        ↓
Book Data
        ↓
Pagination
        ↓
JSON Output
```

### Run

Run the scraper from the project root:

```bash
python -m scraper.scraper
```

The results are saved to:

```text
output/results.json
```

# Running the Playwright Scraper

The Playwright scraper follows this flow:

```text
Async Playwright
        ↓
Chromium
        ↓
Target Website
        ↓
DOM
        ↓
Book Data
        ↓
Pagination
        ↓
JSON Output
```

### Run

```bash
python main.py
```

The results are saved to:

```text
output/playwright_results.json
```
# Proxy Configuration

The Playwright scraper supports proxy configuration using the `PROXY_LIST` environment variable.

### Example

On Windows PowerShell:

```powershell
$env:PROXY_LIST="http://proxy1:8080,http://proxy2:8080,http://proxy3:8080"
```

Multiple proxies can be configured as a comma-separated list.

The scraper uses a round-robin strategy to rotate through the configured proxies:

```text
Proxy 1
   ↓
Proxy 2
   ↓
Proxy 3
   ↓
Proxy 1
   ↓
...
```

The `ProxyManager` component is responsible for managing and rotating through the configured proxies.

Only use proxies that you own or are authorized to use.

Do not commit proxy credentials or private proxy information to the repository.

---

# Error Handling

The project includes error handling for common scraping failures.

## Requests Scraper

The Requests scraper handles:

- Request timeouts
- Connection errors
- HTTP errors
- Request exceptions
- Retry attempts

Example retry flow:

```text
Request
   ↓
Failure
   ↓
Retry
   ↓
Retry
   ↓
Retry
   ↓
Stop if unsuccessful
```

---

## Playwright Scraper

The Playwright scraper handles:

- Navigation timeouts
- Playwright errors
- HTTP error responses
- Missing book information
- Missing rating information
- Missing book URLs
- Proxy-related scraping failures

When multiple authorized proxies are configured, the scraper can attempt to use the next configured proxy after a failed scraping attempt.

---

# Pagination

The target website contains multiple pages of books.

The scraper identifies the next-page link and continues until no next page is available.

```text
Page 1
   ↓
Page 2
   ↓
Page 3
   ↓
...
   ↓
Final Page
   ↓
Stop
```

The results from all pages are combined into a single collection before being saved as JSON.

---

# Testing

The project uses **pytest** for automated testing.

Run the complete test suite:

```bash
python -m pytest -v
```

---

## Run Parser Tests

```bash
python -m pytest tests/test_parser.py -v
```

These tests cover:

- Single book parsing
- Multiple book parsing
- Empty HTML
- Invalid book data

---

## Run Proxy Manager Tests

```bash
python -m pytest tests/test_proxy_manager.py -v
```

These tests cover:

- Proxy rotation
- Empty proxy list
- No configured proxies
- Single proxy configuration

---

## Run Playwright Tests

```bash
python -m pytest tests/test_playwright_scraper.py -v
```

These tests cover:

- Book extraction
- Required fields
- Rating validation
- URL validation
- Pagination
- Final page handling
- Complete website scraping

---

## Run Failure Tests

```bash
python -m pytest tests/test_scraper_failure.py -v
```

These tests cover:

- Invalid URL / HTTP failure
- Page timeout handling

---

# Test Coverage

The test suite validates the main components of the project.

| Component | Tests |
|---|---|
| Parser | Valid data, multiple books, empty HTML, invalid data |
| Proxy Manager | Rotation, empty list, single proxy |
| Playwright | Scraping, fields, pagination, complete scraping |
| Failure Handling | HTTP errors, timeouts |

---

# Architecture

The project separates scraping responsibilities into independent components.

```text
                         Web Scraper
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
          Requests Scraper         Playwright Scraper
                 │                         │
                 ▼                         ▼
           HTTP Response              Browser DOM
                 │                         │
                 ▼                         ▼
           BeautifulSoup                Locators
                 │                         │
                 └────────────┬────────────┘
                              ▼
                         Book Data
                              │
                              ▼
                         JSON Output
```

---

# Component Responsibilities

## `parser.py`

Responsible only for parsing book information from HTML.

```text
HTML
 ↓
BeautifulSoup
 ↓
Structured Book Data
```

---

## `scraper.py`

Responsible for:

- HTTP requests
- Retry handling
- Pagination
- Calling the parser
- Saving results

---

## `playwright_scraper.py`

Responsible for:

- Browser creation
- Playwright automation
- DOM extraction
- Pagination
- Error handling
- Proxy integration
- JSON output

---

## `proxy_manager.py`

Responsible for:

- Managing configured proxies
- Round-robin proxy rotation
- Returning the next configured proxy

---

# JSON Output

The Playwright scraper generates a JSON file containing metadata and scraped records.

Example:

```json
{
    "source": "Books to Scrape",
    "scraper": "Async Playwright",
    "scraped_at": "2026-10-05T00:00:00+00:00",
    "proxy_used": null,
    "records_found": 1000,
    "data": []
}
```

The `data` field contains the scraped book records.

> The example above is only a sample structure. The actual record count depends on the successful scraping run.

The Playwright results are saved to:

```text
output/playwright_results.json
```

The Requests scraper results are saved to:

```text
output/results.json
```

---

# Design Decisions

## Separation of Parsing and Scraping

The HTML parser is kept separate from the HTTP scraper.

This allows the parsing logic to be tested independently using static HTML without making network requests.

---

## Async Playwright

The Playwright implementation uses Python's asynchronous API.

The scraper uses asynchronous functions such as:

```python
async def scrape_books():
    ...
```

and asynchronous operations using:

```python
await
```

This provides a foundation for handling browser automation asynchronously.

---

## Proxy Manager

Proxy handling is separated into its own component rather than embedding rotation logic directly into the scraper.

This makes the proxy behavior easier to test, maintain, and reuse.

---

## Environment Variables

Proxy configuration is read from:

```text
PROXY_LIST
```

This prevents proxy configuration from being hardcoded into the source code.

---

## Error Handling

Network and browser failures are explicitly handled rather than allowing unexpected errors to silently terminate the scraper.

The scraper uses appropriate exception handling and retry logic where applicable.

---

# What This Project Demonstrates

This project demonstrates practical experience with:

- Python
- Web scraping
- HTTP requests
- HTML parsing
- BeautifulSoup
- Async programming
- Playwright
- Browser automation
- DOM interaction
- Pagination
- JSON processing
- Proxy management
- Round-robin proxy rotation
- Retry handling
- Error handling
- Automated testing
- pytest
- pytest-asyncio
- Modular Python project structure

---

# Future Improvements

Possible future improvements include:

- Async HTTP scraping using `aiohttp`
- Configurable concurrency
- Exponential backoff
- Command-line arguments
- External configuration files
- CSV export
- Database storage
- CI/CD integration
- Docker support
- More comprehensive integration tests
- Structured logging configuration

---

# Ethical and Responsible Scraping

This project is intended for educational and authorized scraping and automation purposes.

When building or running scrapers:

- Respect the target website's terms of service.
- Respect applicable `robots.txt` directives.
- Respect rate limits.
- Avoid excessive request volume.
- Do not attempt to bypass authentication or access controls.
- Only use proxy infrastructure that you own or are authorized to use.
- Do not store or commit private credentials.
- Do not commit proxy credentials to the repository.

---

# Author

**Dinesh Aravinth**

QA Automation Engineer | Python | Playwright | API Testing | Test Automation