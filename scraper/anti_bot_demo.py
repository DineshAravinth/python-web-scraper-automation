import asyncio
import logging
import os

from scraper.anti_bot_handler import request_with_retry
from scraper.proxy_manager import ProxyManager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def get_proxy_list():
    proxy_string = os.getenv(
        "PROXY_LIST",
        "",
    ).strip()

    if not proxy_string:
        return []

    return [
        proxy.strip()
        for proxy in proxy_string.split(",")
        if proxy.strip()
    ]


async def main():

    print()
    print("=" * 60)
    print("Anti-Bot Detection & Retry Demonstration")
    print("=" * 60)
    print()

    proxies = get_proxy_list()

    proxy_manager = ProxyManager(proxies)

    print(
        f"Authorized proxies configured: "
        f"{proxy_manager.get_proxy_count()}"
    )

    print()

    # Controlled endpoint that returns HTTP 403.
    #
    # This demonstrates how the scraper handles
    # an access-denied response.
    test_url = "https://httpbin.org/status/403"

    result = await request_with_retry(
        url=test_url,
        proxy_manager=proxy_manager,
        max_retries=3,
        backoff_seconds=2,
    )

    print()
    print("=" * 60)
    print("Final Result")
    print("=" * 60)

    print(f"Status       : {result.status}")
    print(f"HTTP Status  : {result.status_code}")
    print(f"Attempts     : {result.attempts}")
    print(f"Proxy        : {result.proxy}")
    print(f"Error        : {result.error}")

    print("=" * 60)
    print()


if __name__ == "__main__":
    asyncio.run(main())