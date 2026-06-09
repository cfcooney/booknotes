from __future__ import annotations

from datetime import date, datetime, timezone

from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from sqlalchemy import select

from assets.colors import TYPE_FACT, TYPE_NOTE, TYPE_QUOTE
from models import Book, Entry, Person
from models.database import get_session

_TYPE_COLORS = {
    "quote": list(TYPE_QUOTE),
    "note": list(TYPE_NOTE),
    "fact": list(TYPE_FACT),
}
_TYPE_LABELS = {"quote": "Quote", "note": "Note", "fact": "Fact"}
_DEFAULT_COLOR = [0.6, 0.6, 0.6, 1]


def _relative_time(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = (datetime.now(timezone.utc) - dt).days
    if delta == 0:
        return "today"
    if delta == 1:
        return "yesterday"
    return f"{delta} days ago"


def _empty_state(title: str, subtitle: str = "") -> BoxLayout:
    box = BoxLayout(
        orientation="vertical",
        size_hint_y=None,
        height=dp(140),
        spacing=dp(8),
        padding=[dp(32), dp(48)],
    )
    box.add_widget(
        Label(
            text=title,
            font_size="18sp",
            bold=True,
            color=(0.42, 0.40, 0.38, 1),
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(28),
        )
    )
    if subtitle:
        lbl = Label(
            text=subtitle,
            font_size="14sp",
            color=(0.42, 0.40, 0.38, 1),
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(20),
        )
        lbl.bind(size=lambda w, s: setattr(w, "text_size", s))
        box.add_widget(lbl)
    for child in box.children:
        child.bind(size=lambda w, s: setattr(w, "text_size", s))
    return box


class EntryItem(ButtonBehavior, BoxLayout):
    entry_id = NumericProperty(0)
    type_label = StringProperty("")
    type_color = ListProperty([1, 1, 1, 1])
    text_preview = StringProperty("")
    page_text = StringProperty("")
    is_key_takeaway = BooleanProperty(False)
    topic_text = StringProperty("")
    time_text = StringProperty("")


class SectionHeader(BoxLayout):
    header_text = StringProperty("")


class PersonCard(BoxLayout):
    name_text = StringProperty("")
    description_text = StringProperty("")


class AddPersonPopup(Popup):
    def __init__(self, book_id: int, on_save, **kwargs):
        super().__init__(**kwargs)
        self._book_id = book_id
        self._on_save = on_save

    def save(self) -> None:
        name = self.ids.name_input.text.strip()
        if not name:
            return
        description = self.ids.desc_input.text.strip() or None
        session = get_session()
        try:
            session.add(
                Person(book_id=self._book_id, name=name, description=description)
            )
            session.commit()
        finally:
            session.close()
        self.dismiss()
        self._on_save()


class BookScreen(Screen):
    book_id = NumericProperty(0)
    active_tab = StringProperty("entries")
    active_filter = StringProperty("all")
    active_view = StringProperty("journal")

    # Header
    book_title = StringProperty("")
    book_author = StringProperty("")
    book_cover_url = StringProperty("")
    status_label = StringProperty("")
    show_progress = BooleanProperty(False)
    progress_pct = NumericProperty(0.0)
    progress_text = StringProperty("")

    # About tab
    about_year = StringProperty("")
    about_genre = StringProperty("")
    about_isbn = StringProperty("")
    about_start = StringProperty("")
    about_finish = StringProperty("")
    about_quote_count = NumericProperty(0)
    about_note_count = NumericProperty(0)
    about_fact_count = NumericProperty(0)
    is_finished = BooleanProperty(False)

    def on_enter(self, *_) -> None:
        self.active_filter = "all"
        self.active_view = "journal"
        self._load_book()
        self.switch_tab("entries")

    # ── Data loading ───────────────────────────────────────────────────────────

    def _load_book(self) -> None:
        session = get_session()
        try:
            book = session.get(Book, self.book_id)
            if not book:
                return

            self.book_title = book.title
            self.book_author = book.author
            self.book_cover_url = book.cover_url or ""
            self.status_label = book.status.title()
            self.is_finished = book.status == "finished"

            if book.last_page and book.total_pages and book.total_pages > 0:
                self.progress_pct = min(book.last_page / book.total_pages, 1.0)
                self.progress_text = f"p.{book.last_page} of {book.total_pages}"
                self.show_progress = True
            else:
                self.show_progress = False
                self.progress_pct = 0.0
                self.progress_text = ""

            self.about_year = str(book.year) if book.year else ""
            self.about_genre = book.genre or ""
            self.about_isbn = book.isbn or ""
            self.about_start = str(book.start_date) if book.start_date else ""
            self.about_finish = str(book.finish_date) if book.finish_date else ""

            entries = (
                session.execute(select(Entry).where(Entry.book_id == self.book_id))
                .scalars()
                .all()
            )
            self.about_quote_count = sum(1 for e in entries if e.type == "quote")
            self.about_note_count = sum(1 for e in entries if e.type == "note")
            self.about_fact_count = sum(1 for e in entries if e.type == "fact")
        finally:
            session.close()

    # ── Tab switching ──────────────────────────────────────────────────────────

    def switch_tab(self, tab: str) -> None:
        self.active_tab = tab
        self.ids.tab_manager.current = tab
        if tab == "entries":
            self._rebuild_entries()
        elif tab == "characters":
            self._rebuild_characters()

    # ── Entries ────────────────────────────────────────────────────────────────

    def set_filter(self, f: str) -> None:
        self.active_filter = f
        self._rebuild_entries()

    def set_view(self, v: str) -> None:
        self.active_view = v
        self._rebuild_entries()

    def _rebuild_entries(self) -> None:
        entry_list = self.ids.entry_list
        entry_list.clear_widgets()

        session = get_session()
        try:
            stmt = select(Entry).where(Entry.book_id == self.book_id)
            if self.active_filter == "quote":
                stmt = stmt.where(Entry.type == "quote")
            elif self.active_filter == "note":
                stmt = stmt.where(Entry.type == "note")
            elif self.active_filter == "fact":
                stmt = stmt.where(Entry.type == "fact")
            elif self.active_filter == "key":
                stmt = stmt.where(Entry.key_takeaway == True)  # noqa: E712

            entries = session.execute(stmt.order_by(Entry.created_at)).scalars().all()

            if not entries:
                entry_list.add_widget(
                    _empty_state("No entries yet", "Tap + to add your first note")
                )
                return

            if self.active_view == "journal":
                for entry in entries:
                    entry_list.add_widget(self._make_entry_item(entry))
            else:
                for type_key in ("quote", "note", "fact"):
                    group = [e for e in entries if e.type == type_key]
                    if not group:
                        continue
                    entry_list.add_widget(
                        SectionHeader(
                            header_text=_TYPE_LABELS.get(type_key, type_key.title())
                            + "s"
                        )
                    )
                    for entry in group:
                        entry_list.add_widget(self._make_entry_item(entry))
        finally:
            session.close()

    def _make_entry_item(self, entry: Entry) -> EntryItem:
        topic_text = ", ".join(t.name for t in entry.topics)
        item = EntryItem(
            entry_id=entry.id,
            type_label=_TYPE_LABELS.get(entry.type, entry.type.title()),
            type_color=_TYPE_COLORS.get(entry.type, _DEFAULT_COLOR),
            text_preview=entry.text,
            page_text=f"p.{entry.page}" if entry.page else "",
            is_key_takeaway=bool(entry.key_takeaway),
            topic_text=topic_text,
            time_text=_relative_time(entry.created_at) if entry.created_at else "",
        )
        item.bind(on_release=lambda i, eid=entry.id: self.open_entry(eid))
        return item

    def open_entry(self, entry_id: int) -> None:
        pass  # TODO: navigate to Edit Entry screen

    def go_to_add_entry(self) -> None:
        screen = self.manager.get_screen("add_entry")
        screen.book_id = self.book_id
        self.manager.current = "add_entry"

    # ── Characters ─────────────────────────────────────────────────────────────

    def _rebuild_characters(self) -> None:
        char_list = self.ids.character_list
        char_list.clear_widgets()

        session = get_session()
        try:
            persons = (
                session.execute(
                    select(Person)
                    .where(Person.book_id == self.book_id)
                    .order_by(Person.name)
                )
                .scalars()
                .all()
            )

            if not persons:
                char_list.add_widget(_empty_state("No characters added yet"))
                return

            for person in persons:
                char_list.add_widget(
                    PersonCard(
                        name_text=person.name,
                        description_text=person.description or "",
                    )
                )
        finally:
            session.close()

    def open_add_character(self) -> None:
        AddPersonPopup(
            book_id=self.book_id,
            on_save=self._rebuild_characters,
            title="Add Character",
            size_hint=(0.85, None),
            height=dp(320),
        ).open()

    # ── About ──────────────────────────────────────────────────────────────────

    def mark_finished(self) -> None:
        session = get_session()
        try:
            book = session.get(Book, self.book_id)
            if book:
                book.status = "finished"
                book.finish_date = date.today()
                session.commit()
                self.is_finished = True
                self.status_label = "Finished"
                self.about_finish = str(date.today())
        finally:
            session.close()

    def export_notes(self) -> None:
        Popup(
            title="Export Notes",
            content=Label(
                text="Coming soon", halign="center", color=(0.133, 0.145, 0.165, 1)
            ),
            size_hint=(0.6, None),
            height=dp(160),
        ).open()

    def edit_book(self) -> None:
        pass  # TODO: navigate to Edit Book screen

    # ── Navigation ─────────────────────────────────────────────────────────────

    def go_back(self) -> None:
        self.manager.current = "home"
