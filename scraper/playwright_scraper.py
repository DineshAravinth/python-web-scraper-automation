import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

from playwright.async_api import (
    Browser,
    BrowserContext,
    Error as PlaywrightError,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

from scraper.proxy_manager import ProxyManager


BASE_URL = "https://books.toscrape.com/"
OUTPUT_FILE = "output/playwright_results.json"
REQUEST_TIMEOUT = 30000


RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Proxy configuration
# ---------------------------------------------------------

def get_proxy_list():
    """
    Read authorized proxies from the PROXY_LIST
    environment variable.

    Example:
        PROXY_LIST=http://proxy1:8080,http://proxy2:8080
    """

    proxy_string = os.getenv(
        "PROXY_LIST",
        "",
    )

    if not proxy_string:
        return []

    return [
        proxy.strip()
        for proxy in proxy_string.split(",")
        if proxy.strip()
    ]


# ---------------------------------------------------------
# Browser creation
# ---------------------------------------------------------

async def create_browser(
    playwright,
    proxy=None,
) -> Browser:
    """
    Launch Chromium with an optional proxy.
    """

    launch_options: dict[str, Any] = {
        "headless": True,
    }

    if proxy:
        launch_options["proxy"] = {
            "server": proxy,
        }

        logger.info(
            "Launching browser with configured proxy"
        )

    else:
        logger.info(
            "Launching browser with direct connection"
        )

    try:
        return await playwright.chromium.launch(
            **launch_options
        )

    except PlaywrightError as error:
        logger.error(
            "Browser launch failed: %s",
            error,
        )
        raise


# ---------------------------------------------------------
# Scrape one page
# ---------------------------------------------------------

async def scrape_page(
    page: Page,
    url: str,
    timeout: int = REQUEST_TIMEOUT,
):
    """
    Scrape all books from a single page.
    """

    logger.info(
        "Opening: %s",
        url,
    )

    try:
        response = await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=timeout,
        )

        if response is None:
            raise PlaywrightError(
                f"No response received for {url}"
            )

        if not response.ok:
            raise PlaywrightError(
                f"HTTP request failed: "
                f"{response.status} "
                f"{response.status_text}"
            )

    except PlaywrightTimeoutError as error:
        logger.error(
            "Page load timed out: %s | %s",
            url,
            error,
        )
        raise

    except PlaywrightError as error:
        logger.error(
            "Playwright error while opening %s: %s",
            url,
            error,
        )
        raise

    # -----------------------------------------------------
    # Find books on the page
    # -----------------------------------------------------

    books = await page.locator(
        "article.product_pod"
    ).all()

    logger.info(
        "Books found: %s",
        len(books),
    )

    page_data = []

    # -----------------------------------------------------
    # Extract book information
    # -----------------------------------------------------

    for index, book in enumerate(
        books,
        start=1,
    ):

        try:
            title = await book.locator(
                "h3 a"
            ).get_attribute("title")

            if not title:
                raise ValueError(
                    f"Book title missing for book #{index}"
                )

            price = await book.locator(
                "p.price_color"
            ).inner_text()

            availability = (
                await book.locator(
                    "p.instock.availability"
                ).inner_text()
            ).strip()

            rating_classes = await book.locator(
                "p.star-rating"
            ).get_attribute("class")

            if not rating_classes:
                raise ValueError(
                    f"Rating class missing for book #{index}"
                )

            rating_parts = rating_classes.split()

            if len(rating_parts) < 2:
                raise ValueError(
                    f"Invalid rating class for book #{index}"
                )

            rating_name = rating_parts[1]

            rating = RATING_MAP.get(
                rating_name
            )

            if rating is None:
                raise ValueError(
                    f"Unknown rating: {rating_name}"
                )

            relative_url = await book.locator(
                "h3 a"
            ).get_attribute("href")

            if not relative_url:
                raise ValueError(
                    f"Book URL missing for book #{index}"
                )

            book_url = urljoin(
                url,
                relative_url,
            )

            page_data.append(
                {
                    "title": title,
                    "price": price,
                    "availability": availability,
                    "rating": rating,
                    "url": book_url,
                }
            )

        except (
            PlaywrightError,
            ValueError,
        ) as error:

            logger.warning(
                "Unable to parse book #%s: %s",
                index,
                error,
            )

    return page_data


# ---------------------------------------------------------
# Find next page
# ---------------------------------------------------------

async def get_next_page(
    page: Page,
    current_url: str,
):
    """
    Find and return the URL of the next page.
    """

    next_link = page.locator(
        "li.next a"
    )

    if await next_link.count() == 0:
        return None

    next_href = await next_link.get_attribute(
        "href"
    )

    if not next_href:
        return None

    return urljoin(
        current_url,
        next_href,
    )


# ---------------------------------------------------------
# Scrape complete website
# ---------------------------------------------------------

async def scrape_all_pages(
    context: BrowserContext,
):
    """
    Scrape books from all available pages.
    """

    page = await context.new_page()

    current_url = BASE_URL
    all_books = []

    try:

        while current_url:

            logger.info(
                "Scraping page: %s",
                current_url,
            )

            page_books = await scrape_page(
                page,
                current_url,
            )

            all_books.extend(
                page_books
            )

            current_url = await get_next_page(
                page,
                current_url,
            )

    finally:

        await page.close()

    return all_books


# ---------------------------------------------------------
# Save JSON
# ---------------------------------------------------------

def save_results(
    books,
    proxy_used=None,
):
    """
    Save scraped data as JSON.
    """

    result = {
        "source": "Books to Scrape",
        "scraper": "Async Playwright",
        "scraped_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "proxy_used": proxy_used,
        "records_found": len(books),
        "data": books,
    }

    os.makedirs(
        "output",
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False,
        )

    logger.info(
        "Results saved to %s",
        OUTPUT_FILE,
    )


# ---------------------------------------------------------
# Scrape using one proxy
# ---------------------------------------------------------

async def scrape_with_proxy(
    playwright,
    proxy=None,
):
    """
    Launch a browser with the selected proxy,
    scrape the website, and clean up resources.
    """

    browser = None
    context = None

    try:
        browser = await create_browser(
            playwright,
            proxy=proxy,
        )

        context = await browser.new_context()

        books = await scrape_all_pages(
            context,
        )

        return books

    except PlaywrightTimeoutError:
        logger.error(
            "Scraping timed out."
        )
        raise

    except PlaywrightError as error:
        logger.error(
            "Playwright scraping failed: %s",
            error,
        )
        raise

    finally:

        if context:
            await context.close()

        if browser:
            await browser.close()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

async def main():
    """
    Main entry point for the Playwright scraper.
    """

    proxy_list = get_proxy_list()

    proxy_manager = ProxyManager(
        proxy_list
    )

    if proxy_manager.has_proxies():

        max_attempts = (
            proxy_manager.get_proxy_count()
        )

    else:

        max_attempts = 1

    logger.info(
        "Maximum attempts: %s",
        max_attempts,
    )

    async with async_playwright() as playwright:

        for attempt in range(
            1,
            max_attempts + 1,
        ):

            proxy = proxy_manager.get_next_proxy()

            logger.info(
                "Scraping attempt %s/%s",
                attempt,
                max_attempts,
            )

            try:

                books = await scrape_with_proxy(
                    playwright,
                    proxy=proxy,
                )

                if not books:
                    raise ValueError(
                        "Scraper returned zero books"
                    )

                save_results(
                    books,
                    proxy_used=proxy,
                )

                logger.info(
                    "Scraping completed successfully. "
                    "Total records: %s",
                    len(books),
                )

                return

            except (
                PlaywrightTimeoutError,
                PlaywrightError,
            ) as error:

                logger.error(
                    "Scraping attempt %s failed: %s",
                    attempt,
                    error,
                )

                if attempt < max_attempts:

                    logger.info(
                        "Trying the next configured proxy..."
                    )

                else:

                    logger.error(
                        "All configured attempts failed."
                    )

                    raise


if __name__ == "__main__":
    asyncio.run(main())