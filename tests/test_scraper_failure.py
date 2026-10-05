import pytest

from playwright.async_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
)

from scraper.playwright_scraper import scrape_page


@pytest.mark.asyncio
async def test_scrape_page_invalid_url(playwright):
    browser = await playwright.chromium.launch(
        headless=True
    )

    page = await browser.new_page()

    try:
        invalid_url = (
            "https://books.toscrape.com/"
            "this-page-does-not-exist"
        )

        with pytest.raises(PlaywrightError):
            await scrape_page(
                page,
                invalid_url,
            )

    finally:
        await browser.close()


@pytest.mark.asyncio
async def test_scrape_page_timeout(playwright):
    browser = await playwright.chromium.launch(
        headless=True
    )

    page = await browser.new_page()

    try:
        with pytest.raises(PlaywrightTimeoutError):
            await scrape_page(
                page,
                "https://books.toscrape.com/",
                timeout=1,
            )

    finally:
        await browser.close()