import pytest

from scraper.playwright_scraper import (
    get_next_page,
    scrape_all_pages,
    scrape_page,
)


BASE_URL = "https://books.toscrape.com/"


@pytest.mark.asyncio
async def test_scrape_books(playwright):
    browser = await playwright.chromium.launch(
        headless=True
    )

    page = await browser.new_page()

    try:
        books = await scrape_page(
            page,
            BASE_URL,
        )

        assert len(books) == 20

        first_book = books[0]

        assert first_book["title"]
        assert first_book["price"]
        assert first_book["availability"]

        assert first_book["rating"] in range(1, 6)

        assert first_book["url"].startswith(
            "https://"
        )

    finally:
        await browser.close()


@pytest.mark.asyncio
async def test_scrape_books_have_required_fields(playwright):
    browser = await playwright.chromium.launch(
        headless=True
    )

    page = await browser.new_page()

    try:
        books = await scrape_page(
            page,
            BASE_URL,
        )

        assert len(books) == 20

        required_fields = {
            "title",
            "price",
            "availability",
            "rating",
            "url",
        }

        for book in books:
            assert required_fields.issubset(
                book.keys()
            )

            assert isinstance(
                book["title"],
                str,
            )

            assert isinstance(
                book["price"],
                str,
            )

            assert isinstance(
                book["availability"],
                str,
            )

            assert isinstance(
                book["rating"],
                int,
            )

            assert 1 <= book["rating"] <= 5

            assert book["url"].startswith(
                "https://"
            )

    finally:
        await browser.close()


@pytest.mark.asyncio
async def test_get_next_page(playwright):
    browser = await playwright.chromium.launch(
        headless=True
    )

    page = await browser.new_page()

    try:
        await page.goto(
            BASE_URL,
            wait_until="domcontentloaded",
        )

        next_url = await get_next_page(
            page,
            BASE_URL,
        )

        assert next_url == (
            "https://books.toscrape.com/"
            "catalogue/page-2.html"
        )

    finally:
        await browser.close()


@pytest.mark.asyncio
async def test_final_page_has_no_next_page(playwright):
    browser = await playwright.chromium.launch(
        headless=True
    )

    page = await browser.new_page()

    try:
        final_page_url = (
            "https://books.toscrape.com/"
            "catalogue/page-50.html"
        )

        await page.goto(
            final_page_url,
            wait_until="domcontentloaded",
        )

        next_url = await get_next_page(
            page,
            final_page_url,
        )

        assert next_url is None

    finally:
        await browser.close()


@pytest.mark.asyncio
async def test_scrape_all_pages(playwright):
    browser = await playwright.chromium.launch(
        headless=True
    )

    context = await browser.new_context()

    try:
        books = await scrape_all_pages(
            context,
        )

        assert len(books) == 1000

        assert all(
            book["title"]
            for book in books
        )

    finally:
        await context.close()
        await browser.close()