from scraper.parser import parse_books


def test_parse_books():
    html = """
    <html>
        <body>
            <article class="product_pod">
                <h3>
                    <a
                        href="catalogue/test-book_1/index.html"
                        title="Test Book">
                    </a>
                </h3>

                <p class="price_color">£20.00</p>

                <p class="instock availability">
                    In stock
                </p>

                <p class="star-rating Three"></p>
            </article>
        </body>
    </html>
    """

    books = parse_books(
        html,
        "https://books.toscrape.com/",
    )

    assert len(books) == 1

    book = books[0]

    assert book["title"] == "Test Book"
    assert book["price"] == "£20.00"
    assert book["availability"] == "In stock"
    assert book["rating"] == 3
    assert book["url"] == (
        "https://books.toscrape.com/"
        "catalogue/test-book_1/index.html"
    )


def test_parse_multiple_books():
    html = """
    <article class="product_pod">
        <h3>
            <a
                href="book1.html"
                title="Book One">
            </a>
        </h3>

        <p class="price_color">£10.00</p>

        <p class="instock availability">
            In stock
        </p>

        <p class="star-rating One"></p>
    </article>

    <article class="product_pod">
        <h3>
            <a
                href="book2.html"
                title="Book Two">
            </a>
        </h3>

        <p class="price_color">£20.00</p>

        <p class="instock availability">
            In stock
        </p>

        <p class="star-rating Five"></p>
    </article>
    """

    books = parse_books(
        html,
        "https://books.toscrape.com/",
    )

    assert len(books) == 2

    assert books[0]["title"] == "Book One"
    assert books[0]["rating"] == 1

    assert books[1]["title"] == "Book Two"
    assert books[1]["rating"] == 5


def test_parse_empty_html():
    html = """
    <html>
        <body>
        </body>
    </html>
    """

    books = parse_books(
        html,
        "https://books.toscrape.com/",
    )

    assert books == []


def test_parse_invalid_book():
    html = """
    <article class="product_pod">
        <h3>
            <a title="Incomplete Book"></a>
        </h3>
    </article>
    """

    books = parse_books(
        html,
        "https://books.toscrape.com/",
    )

    assert books == []