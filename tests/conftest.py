import pytest_asyncio
from playwright.async_api import async_playwright


@pytest_asyncio.fixture
async def playwright():
    async with async_playwright() as playwright:
        yield playwright