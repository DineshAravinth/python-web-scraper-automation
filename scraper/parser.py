from urllib.parse import urljoin

from bs4 import BeautifulSoup


RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def parse_books(html, current_url):
    """
    Extract book information from HTML.
    """

    soup = BeautifulSoup(html, "html.parser")

    books = soup.find_all(
        "article",
        class_="product_pod",
    )

    books_data = []

    for book in books:
        try:
            title = book.h3.a["title"]

            price = book.find(
                "p",
                class_="price_color",
            ).text

            availability = book.find(
                "p",
                class_="instock availability",
            ).text.strip()

            rating_classes = book.find(
                "p",
                class_="star-rating",
            )["class"]

            rating = RATING_MAP[rating_classes[1]]

            relative_url = book.h3.a["href"]

            book_url = urljoin(
                current_url,
                relative_url,
            )

            book_data = {
                "title": title,
                "price": price,
                "availability": availability,
                "rating": rating,
                "url": book_url,
            }

            books_data.append(book_data)

        except (AttributeError, KeyError, TypeError) as error:
            print(f"Unable to parse a book: {error}")

    return books_data