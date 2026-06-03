from __future__ import annotations

import threading
from datetime import date

from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.screenmanager import Screen

from models import Book
from models.database import get_session
from services.openlibrary import BookMetadata, search_by_title_author

GENRES = [
    "Literary Fiction",
    "Thriller",
    "Mystery",
    "Science Fiction",
    "Fantasy",
    "Historical Fiction",
    "Biography",
    "History",
    "Science",
    "Philosophy",
    "Psychology",
    "Business",
    "Other",
]


class AddBookScreen(Screen):
    title_text = StringProperty("")
    author_text = StringProperty("")
    # "fiction" | "nonfiction" | "" (empty = not yet chosen)
    fiction_selected = StringProperty("")
    year_text = StringProperty("")
    genre_text = StringProperty("Select genre")
    fetching = BooleanProperty(False)
    fetch_status = StringProperty("")

    GENRES = GENRES
    _metadata: BookMetadata | None = None

    def on_enter(self, *_) -> None:
        self._reset_form()

    def _reset_form(self) -> None:
        self.title_text = ""
        self.author_text = ""
        self.fiction_selected = ""
        self.year_text = ""
        self.genre_text = "Select genre"
        self.fetch_status = ""
        self.fetching = False
        self._metadata = None

        ids = self.ids
        ids.title_input.text = ""
        ids.author_input.text = ""
        ids.year_input.text = ""
        ids.genre_spinner.text = "Select genre"
        ids.preview_cover.source = ""
        ids.content_manager.current = "form"

    # ── Navigation ────────────────────────────────────────────────────────────

    def go_back(self) -> None:
        self.manager.current = "home"

    # ── Form interactions ─────────────────────────────────────────────────────

    def select_fiction(self, value: str) -> None:
        self.fiction_selected = value

    # ── Metadata fetch ────────────────────────────────────────────────────────

    def fetch_metadata(self) -> None:
        title = self.title_text.strip()
        author = self.author_text.strip()
        if not title or not author:
            return
        self.fetching = True
        self.fetch_status = ""

        def _fetch() -> None:
            result = search_by_title_author(title, author)
            Clock.schedule_once(lambda dt: self._on_metadata_fetched(result))

        threading.Thread(target=_fetch, daemon=True).start()

    def _on_metadata_fetched(self, metadata: BookMetadata | None) -> None:
        self.fetching = False
        if metadata is None:
            self.fetch_status = "No metadata found"
            return
        self._metadata = metadata
        self._populate_preview(metadata)
        self.ids.content_manager.current = "preview"

    def _populate_preview(self, metadata: BookMetadata) -> None:
        ids = self.ids
        ids.preview_title.text = metadata.title or ""
        ids.preview_author.text = f"by {metadata.author}" if metadata.author else ""
        ids.preview_year.text = str(metadata.year) if metadata.year else ""
        ids.preview_genre.text = metadata.genre or ""
        ids.preview_cover.source = metadata.cover_url or ""

    # ── Preview interactions ──────────────────────────────────────────────────

    def use_metadata(self) -> None:
        if not self._metadata:
            return
        m = self._metadata
        ids = self.ids
        ids.title_input.text = m.title or ""
        ids.author_input.text = m.author or ""
        self.title_text = m.title or ""
        self.author_text = m.author or ""
        if m.year:
            ids.year_input.text = str(m.year)
            self.year_text = str(m.year)
        if m.genre and m.genre in GENRES:
            ids.genre_spinner.text = m.genre
            self.genre_text = m.genre
        ids.content_manager.current = "form"

    def skip_metadata(self) -> None:
        self.ids.content_manager.current = "form"

    # ── Save ──────────────────────────────────────────────────────────────────

    def save_book(self) -> None:
        title = self.title_text.strip()
        author = self.author_text.strip()
        if not title or not author or not self.fiction_selected:
            return

        fiction = self.fiction_selected == "fiction"
        genre = self.genre_text if self.genre_text != "Select genre" else None
        year = int(self.year_text) if self.year_text.strip().isdigit() else None
        m = self._metadata

        book_id = None
        session = get_session()
        try:
            book = Book(
                title=title,
                author=author,
                fiction=fiction,
                genre=genre,
                year=year,
                cover_url=m.cover_url if m else None,
                isbn=m.isbn if m else None,
                total_pages=m.total_pages if m else None,
                status="reading",
                start_date=date.today(),
            )
            session.add(book)
            session.commit()
            book_id = book.id  # capture before session closes
        finally:
            session.close()

        book_screen = self.manager.get_screen("book")
        book_screen.book_id = book_id
        self.manager.current = "book"
