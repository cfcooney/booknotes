from __future__ import annotations

from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from sqlalchemy import select

from models import Book
from models.database import get_session


class BookCard(BoxLayout):
    title_text = StringProperty("")
    author_text = StringProperty("")


class HomeScreen(Screen):
    def on_enter(self, *_) -> None:
        self.refresh_book_list()

    def refresh_book_list(self) -> None:
        book_list = self.ids.book_list
        book_list.clear_widgets()
        session = get_session()
        try:
            books = session.execute(select(Book).order_by(Book.title)).scalars().all()
            for book in books:
                book_list.add_widget(
                    BookCard(title_text=book.title, author_text=book.author)
                )
        finally:
            session.close()

    def go_to_add_book(self) -> None:
        self.manager.current = "add_book"
