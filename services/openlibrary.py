from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)

_SEARCH_URL = "https://openlibrary.org/search.json"
_ISBN_URL = "https://openlibrary.org/isbn/{isbn}.json"
_AUTHOR_URL = "https://openlibrary.org{key}.json"
_COVER_URL = "https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
_TIMEOUT = 5


@dataclass
class BookMetadata:
    title: str
    author: str
    year: int | None
    genre: str | None
    cover_url: str | None
    isbn: str | None
    total_pages: int | None


def search_by_title_author(title: str, author: str) -> BookMetadata | None:
    """Search Open Library by title and author; return the best match or None."""
    try:
        response = requests.get(
            _SEARCH_URL,
            params={"title": title, "author": author, "limit": 1},
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.warning("Open Library search failed: %s", exc)
        return None

    docs = data.get("docs", [])
    if not docs:
        logger.debug("No results for title=%r author=%r", title, author)
        return None

    doc = docs[0]

    cover_id = doc.get("cover_i")
    author_names = doc.get("author_name", [])
    isbns = doc.get("isbn", [])

    return BookMetadata(
        title=doc.get("title", title),
        author=author_names[0] if author_names else author,
        year=doc.get("first_publish_year"),
        genre=None,  # Open Library search does not expose a genre field
        cover_url=_COVER_URL.format(cover_id=cover_id) if cover_id else None,
        isbn=isbns[0] if isbns else None,
        total_pages=doc.get("number_of_pages_median"),
    )


def search_by_isbn(isbn: str) -> BookMetadata | None:
    """Fetch book metadata from Open Library by ISBN; return None if not found."""
    try:
        response = requests.get(
            _ISBN_URL.format(isbn=isbn),
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.warning("Open Library ISBN lookup failed for %r: %s", isbn, exc)
        return None

    publish_date = data.get("publish_date", "")
    year_match = re.search(r"\d{4}", publish_date)

    covers = data.get("covers", [])

    return BookMetadata(
        title=data.get("title", ""),
        author=_author_from_edition(data),
        year=int(year_match.group()) if year_match else None,
        genre=None,
        cover_url=_COVER_URL.format(cover_id=covers[0]) if covers else None,
        isbn=isbn,
        total_pages=data.get("number_of_pages"),
    )


def _resolve_author(authors: list[dict]) -> str:
    """Follow the first author key to fetch the author's name."""
    if not authors:
        return ""
    key = authors[0].get("key", "")
    if not key:
        return ""
    try:
        response = requests.get(
            _AUTHOR_URL.format(key=key),
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
        return response.json().get("name", "")
    except requests.RequestException as exc:
        logger.warning("Failed to resolve author %r: %s", key, exc)
        return ""


def _author_from_edition(edition: dict) -> str:
    """Resolve author name from an edition dict.

    Editions often omit ``authors`` and reference a Work instead.
    Falls back to fetching the Work and resolving from there.
    """
    authors = edition.get("authors", [])
    if authors:
        return _resolve_author(authors)

    works = edition.get("works", [])
    if not works:
        return ""
    work_key = works[0].get("key", "")
    if not work_key:
        return ""
    try:
        response = requests.get(
            _AUTHOR_URL.format(key=work_key),
            timeout=_TIMEOUT,
        )
        response.raise_for_status()
        work_authors = response.json().get("authors", [])
        # Work author entries look like {"author": {"key": "/authors/OL22242A"}, ...}
        return _resolve_author([a.get("author", a) for a in work_authors])
    except requests.RequestException as exc:
        logger.warning("Failed to resolve work %r: %s", work_key, exc)
        return ""


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    logging.basicConfig(
        level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s"
    )

    print("--- search_by_title_author ---")
    result = search_by_title_author("The Brothers Karamazov", "Dostoevsky")
    print(result)

    print("\n--- search_by_isbn (9780374528379) ---")
    result = search_by_isbn("9780374528379")
    print(result)
