import asyncio
import logging
from dataclasses import dataclass

import requests

from scraper.proxy_manager import ProxyManager


logger = logging.getLogger(__name__)


@dataclass
class AntiBotResult:
    status: str
    status_code: int | None
    attempts: int
    proxy: str | None
    error: str | None = None


def is_block_response(status_code: int) -> bool:
    """
    Identify HTTP responses commonly used for
    access blocking or rate limiting.

    This detects the response.
    It does not attempt to bypass it.
    """
    return status_code in {403, 429}


async def request_with_retry(
    url: str,
    proxy_manager: ProxyManager,
    max_retries: int = 3,
    backoff_seconds: int = 2,
) -> AntiBotResult:

    for attempt in range(1, max_retries + 1):

        proxy = proxy_manager.get_next_proxy()

        logger.info(
            "Request started | Attempt: %s/%s | Proxy: %s",
            attempt,
            max_retries,
            proxy or "direct",
        )

        print(
            f"Request started | "
            f"Attempt: {attempt}/{max_retries} | "
            f"Proxy: {proxy or 'direct'}"
        )

        proxies = None

        if proxy:
            proxies = {
                "http": proxy,
                "https": proxy,
            }

        try:
            response = await asyncio.to_thread(
                requests.get,
                url,
                proxies=proxies,
                timeout=10,
            )

            print(
                f"Response: {response.status_code}"
            )

            if is_block_response(response.status_code):

                print(
                    "Anti-bot/rate-limit response detected"
                )

                if attempt < max_retries:

                    print(
                        f"Retry: {attempt}/{max_retries}"
                    )

                    delay = backoff_seconds * (
                        2 ** (attempt - 1)
                    )

                    print(
                        f"Backoff: {delay} seconds"
                    )

                    await asyncio.sleep(delay)

                    print("Proxy rotated")

                    print("Retry started")

                    continue

                return AntiBotResult(
                    status="blocked",
                    status_code=response.status_code,
                    attempts=attempt,
                    proxy=proxy,
                    error="Maximum retries reached",
                )

            response.raise_for_status()

            print("Request successful")

            return AntiBotResult(
                status="success",
                status_code=response.status_code,
                attempts=attempt,
                proxy=proxy,
            )

        except requests.RequestException as error:

            print(
                f"Request error: {error}"
            )

            if attempt < max_retries:

                print(
                    f"Retry: {attempt}/{max_retries}"
                )

                delay = backoff_seconds * (
                    2 ** (attempt - 1)
                )

                print(
                    f"Backoff: {delay} seconds"
                )

                await asyncio.sleep(delay)

                print("Proxy rotated")
                print("Retry started")

                continue

            return AntiBotResult(
                status="failed",
                status_code=None,
                attempts=attempt,
                proxy=proxy,
                error=str(error),
            )

    return AntiBotResult(
        status="failed",
        status_code=None,
        attempts=max_retries,
        proxy=None,
        error="Unexpected execution path",
    )