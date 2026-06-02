from __future__ import annotations

from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from sqlalchemy import select

from models import Book
from services.database import get_session


class BookCard(BoxLayout):
    title_text = StringProperty("")
    author_text = StringProperty("")


class AddBookPopup(Popup):
    def __init__(self, on_save: callable, **kwargs) -> None:
        self._on_save = on_save
        super().__init__(**kwargs)

    def save(self) -> None:
        title = self.ids.title_input.text.strip()
        author = self.ids.author_input.text.strip()
        if title and author:
            self._on_save(title, author)
            self.dismiss()


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

    def open_add_book_popup(self) -> None:
        AddBookPopup(on_save=self.save_book).open()

    def save_book(self, title: str, author: str) -> None:
        session = get_session()
        try:
            session.add(Book(title=title, author=author))
            session.commit()
        finally:
            session.close()
        self.refresh_book_list()
