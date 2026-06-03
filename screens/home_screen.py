from __future__ import annotations

from datetime import date

from kivy.properties import NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from sqlalchemy import select

from models import Book, Entry
from models.database import get_session


class BookCard(ButtonBehavior, BoxLayout):
    title_text = StringProperty("")
    author_text = StringProperty("")
    cover_url = StringProperty("")
    genre_text = StringProperty("")
    last_entry_text = StringProperty("")
    book_id = NumericProperty(0)


class EmptyState(BoxLayout):
    pass


class HomeScreen(Screen):
    active_tab = StringProperty("reading")

    def on_enter(self, *_) -> None:
        self.refresh_book_list()

    def switch_tab(self, tab: str) -> None:
        self.active_tab = tab
        self.refresh_book_list()

    def refresh_book_list(self) -> None:
        book_list = self.ids.book_list
        book_list.clear_widgets()

        session = get_session()
        try:
            stmt = select(Book)
            if self.active_tab == "reading":
                stmt = stmt.where(Book.status == "reading").order_by(Book.title)
            else:
                stmt = stmt.order_by(Book.created_at.desc())

            books = session.execute(stmt).scalars().all()

            if not books:
                book_list.add_widget(EmptyState())
                return

            for book in books:
                latest = (
                    session.execute(
                        select(Entry)
                        .where(Entry.book_id == book.id)
                        .order_by(Entry.created_at.desc())
                        .limit(1)
                    )
                    .scalars()
                    .first()
                )

                last_entry_text = ""
                if latest and latest.created_at:
                    delta = (date.today() - latest.created_at.date()).days
                    if delta == 0:
                        last_entry_text = "Last note: today"
                    elif delta == 1:
                        last_entry_text = "Last note: yesterday"
                    else:
                        last_entry_text = f"Last note: {delta} days ago"

                card = BookCard(
                    title_text=book.title,
                    author_text=book.author,
                    cover_url=book.cover_url or "",
                    genre_text=book.genre or "",
                    last_entry_text=last_entry_text,
                    book_id=book.id,
                )
                card.bind(on_release=lambda c, bid=book.id: self.go_to_book(bid))
                book_list.add_widget(card)
        finally:
            session.close()

    def go_to_add_book(self) -> None:
        self.manager.current = "add_book"

    def go_to_book(self, book_id: int) -> None:
        screen = self.manager.get_screen("book")
        screen.book_id = book_id
        self.manager.current = "book"
