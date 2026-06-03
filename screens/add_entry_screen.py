from __future__ import annotations

from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from sqlalchemy import select

from models import Book, Entry, Topic
from models.database import get_session

_HINTS = {
    "quote": "Enter the quote exactly as written...",
    "note": "Write your thought or observation...",
    "fact": "State the fact or assertion...",
}


class TopicChip(ButtonBehavior, BoxLayout):
    topic_name = StringProperty("")


class AddEntryScreen(Screen):
    book_id = NumericProperty(0)
    entry_type = StringProperty("note")
    entry_text = StringProperty("")
    details_expanded = BooleanProperty(False)
    importance = NumericProperty(0)  # 0=unset, 1/2/3
    is_key_takeaway = BooleanProperty(False)

    def on_enter(self, *_) -> None:
        self._reset_form()
        self._load_topic_chips()

    def _reset_form(self) -> None:
        self.entry_type = "note"
        self.entry_text = ""
        self.details_expanded = False
        self.importance = 0
        self.is_key_takeaway = False
        ids = self.ids
        ids.text_input.text = ""
        ids.page_input.text = ""
        ids.topics_input.text = ""

    def _load_topic_chips(self) -> None:
        chip_row = self.ids.topic_chips
        chip_row.clear_widgets()
        session = get_session()
        try:
            topics = session.execute(select(Topic).order_by(Topic.name)).scalars().all()
            for topic in topics:
                name = topic.name
                chip = TopicChip(topic_name=name)
                chip.bind(on_release=lambda c, n=name: self._add_topic(n))
                chip_row.add_widget(chip)
        finally:
            session.close()

    # ── Form interactions ──────────────────────────────────────────────────────

    def select_type(self, type_: str) -> None:
        self.entry_type = type_

    def toggle_details(self) -> None:
        self.details_expanded = not self.details_expanded

    def set_importance(self, level: int) -> None:
        # Tapping the same star again resets to 0
        self.importance = 0 if self.importance == level else level

    def toggle_key_takeaway(self) -> None:
        self.is_key_takeaway = not self.is_key_takeaway

    def _add_topic(self, name: str) -> None:
        current = self.ids.topics_input.text
        existing = [t.strip() for t in current.split(",") if t.strip()]
        if name not in existing:
            existing.append(name)
            self.ids.topics_input.text = ", ".join(existing)

    # ── Save ──────────────────────────────────────────────────────────────────

    def save_entry(self) -> None:
        text = self.ids.text_input.text.strip()
        if not text:
            return

        page_str = self.ids.page_input.text.strip()
        page = int(page_str) if page_str.isdigit() else None

        topics_raw = self.ids.topics_input.text.strip()
        topic_names = [t.strip() for t in topics_raw.split(",") if t.strip()]

        importance = self.importance if self.importance > 0 else None

        session = get_session()
        try:
            topics: list[Topic] = []
            for name in topic_names:
                topic = (
                    session.execute(select(Topic).where(Topic.name == name))
                    .scalars()
                    .first()
                )
                if not topic:
                    topic = Topic(name=name)
                    session.add(topic)
                    session.flush()
                topics.append(topic)

            entry = Entry(
                book_id=self.book_id,
                type=self.entry_type,
                text=text,
                page=page,
                key_takeaway=self.is_key_takeaway,
                importance=importance,
            )
            session.add(entry)
            session.flush()

            for topic in topics:
                entry.topics.append(topic)

            if page is not None:
                book = session.get(Book, self.book_id)
                if book and (book.last_page is None or page > book.last_page):
                    book.last_page = page

            session.commit()
        finally:
            session.close()

        self.manager.current = "book"

    # ── Navigation ─────────────────────────────────────────────────────────────

    def go_back(self) -> None:
        self.manager.current = "book"
