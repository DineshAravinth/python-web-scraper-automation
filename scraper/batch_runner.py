import asyncio
import json
import logging
import time
from pathlib import Path

from playwright.async_api import async_playwright

from scraper.playwright_scraper import (
    BASE_URL,
    create_browser,
    scrape_all_pages,
)
from scraper.proxy_manager import ProxyManager


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BATCH_URLS = [
    BASE_URL,
    BASE_URL,
    BASE_URL,
    BASE_URL,
    BASE_URL,
]

MAX_CONCURRENCY = 3

OUTPUT_FILE = Path("output/batch_results.json")


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Proxy configuration
# --------------------------------------------------

def get_proxy_list():
    """
    Read authorized proxies from the PROXY_LIST
    environment variable.

    Example:

    $env:PROXY_LIST="http://proxy1:8080,http://proxy2:8080"
    """

    proxy_list = []

    import os

    proxy_string = os.getenv("PROXY_LIST", "").strip()

    if proxy_string:
        proxy_list = [
            proxy.strip()
            for proxy in proxy_string.split(",")
            if proxy.strip()
        ]

    return proxy_list


# --------------------------------------------------
# Single batch task
# --------------------------------------------------

async def scrape_single_task(
    task_id,
    url,
    playwright,
    proxy_manager,
    semaphore,
):
    """
    Execute one scraping task.

    The semaphore limits the number of concurrent
    scraping jobs.
    """

    async with semaphore:

        start_time = time.perf_counter()

        proxy = proxy_manager.get_next_proxy()

        logger.info(
            "[Task %s] Started | Proxy: %s | URL: %s",
            task_id,
            proxy or "Direct connection",
            url,
        )

        browser = None
        context = None

        try:
            # Create browser with the selected proxy
            browser = await create_browser(
                playwright,
                proxy=proxy,
            )

            # Create a browser context.
            # The context represents the session for this task.
            context = await browser.new_context()

            books = await scrape_all_pages(context)

            duration = round(
                time.perf_counter() - start_time,
                2,
            )

            logger.info(
                "[Task %s] Completed | Records: %s | Duration: %ss",
                task_id,
                len(books),
                duration,
            )

            return {
                "task_id": task_id,
                "url": url,
                "status": "success",
                "proxy": proxy or "direct",
                "records_found": len(books),
                "duration_seconds": duration,
                "data": books,
            }

        except Exception as error:

            duration = round(
                time.perf_counter() - start_time,
                2,
            )

            logger.error(
                "[Task %s] Failed | Error: %s",
                task_id,
                error,
            )

            return {
                "task_id": task_id,
                "url": url,
                "status": "failed",
                "proxy": proxy or "direct",
                "records_found": 0,
                "duration_seconds": duration,
                "error": str(error),
                "data": [],
            }

        finally:

            if context:
                await context.close()

            if browser:
                await browser.close()


# --------------------------------------------------
# Batch runner
# --------------------------------------------------

async def run_batch():

    print()
    print("=" * 60)
    print("Python Scraping & Automation - Concurrent Batch Runner")
    print("=" * 60)
    print()

    print(f"Batch size: {len(BATCH_URLS)}")
    print(f"Concurrency limit: {MAX_CONCURRENCY}")
    print()

    proxy_list = get_proxy_list()

    proxy_manager = ProxyManager(proxy_list)

    if proxy_manager.has_proxies():

        print(
            f"Authorized proxies configured: "
            f"{proxy_manager.get_proxy_count()}"
        )

    else:

        print("No proxy configured - using direct connection")

    print()

    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    results = []

    async with async_playwright() as playwright:

        tasks = []

        for task_id, url in enumerate(BATCH_URLS, start=1):

            task = scrape_single_task(
                task_id=task_id,
                url=url,
                playwright=playwright,
                proxy_manager=proxy_manager,
                semaphore=semaphore,
            )

            tasks.append(task)

        # Run all tasks concurrently.
        # The semaphore controls how many actually run
        # at the same time.
        results = await asyncio.gather(*tasks)

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    successful = [
        result
        for result in results
        if result["status"] == "success"
    ]

    failed = [
        result
        for result in results
        if result["status"] == "failed"
    ]

    total_records = sum(
        result["records_found"]
        for result in results
    )

    # --------------------------------------------------
    # Save JSON
    # --------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "project": "Python Scraping & Automation",
        "execution_type": "concurrent_batch",
        "batch_size": len(BATCH_URLS),
        "concurrency_limit": MAX_CONCURRENCY,
        "successful_tasks": len(successful),
        "failed_tasks": len(failed),
        "total_records": total_records,
        "results": results,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False,
        )

    # --------------------------------------------------
    # Terminal summary
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("Batch execution completed")
    print("=" * 60)

    print(f"Total tasks     : {len(results)}")
    print(f"Successful      : {len(successful)}")
    print(f"Failed          : {len(failed)}")
    print(f"Total records   : {total_records}")

    print()
    print(f"Results saved to: {OUTPUT_FILE}")
    print("=" * 60)
    print()


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    asyncio.run(run_batch())