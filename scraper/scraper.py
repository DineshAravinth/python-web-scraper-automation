import json
import logging
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from scraper.parser import parse_books


BASE_URL = "https://books.toscrape.com/"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
OUTPUT_FILE = "output/results.json"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def fetch_page(session, url):
    """
    Fetch a webpage with retry and error handling.
    """

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            logger.info(
                "Fetching page: %s | Attempt: %s",
                url,
                attempt,
            )

            response = session.get(
                url,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            response.encoding = "utf-8"

            return response.text

        except requests.Timeout:
            logger.warning(
                "Request timed out: %s",
                url,
            )

        except requests.ConnectionError:
            logger.warning(
                "Connection error: %s",
                url,
            )

        except requests.HTTPError as error:
            logger.error(
                "HTTP error for %s: %s",
                url,
                error,
            )
            break

        except requests.RequestException as error:
            logger.error(
                "Request failed for %s: %s",
                url,
                error,
            )
            break

        if attempt < MAX_RETRIES:
            logger.info("Retrying...")
            time.sleep(2)

    return None


def scrape_books():
    """
    Scrape books from all available pages.
    """

    current_url = BASE_URL
    books_data = []

    with requests.Session() as session:

        while current_url:

            logger.info(
                "Starting page: %s",
                current_url,
            )

            html = fetch_page(
                session,
                current_url,
            )

            if html is None:
                logger.error(
                    "Unable to fetch page. Stopping scraper."
                )
                break

            page_books = parse_books(
                html,
                current_url,
            )

            logger.info(
                "Books found on page: %s",
                len(page_books),
            )

            books_data.extend(page_books)



            soup = BeautifulSoup(
                html,
                "html.parser",
            )

            next_button = soup.find(
                "li",
                class_="next",
            )

            if next_button:

                next_page = next_button.a["href"]

                current_url = urljoin(
                    current_url,
                    next_page,
                )

            else:
                current_url = None

    return books_data


def save_results(books_data):
    """
    Save scraped data as JSON.
    """

    output = {
        "source": "Books to Scrape",
        "scraper": "Requests + BeautifulSoup",
        "records_found": len(books_data),
        "data": books_data,
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

    logger.info(
        "Data saved to %s",
        OUTPUT_FILE,
    )


if __name__ == "__main__":

    logger.info("Requests scraper started")

    books = scrape_books()

    logger.info(
        "Scraping completed. Total records: %s",
        len(books),
    )

    save_results(books)