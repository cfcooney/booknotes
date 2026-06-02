from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .associations import entry_people, entry_topics
from .base import Base

if TYPE_CHECKING:
    from .book import Book
    from .person import Person
    from .topic import Topic


class Entry(Base):
    """A single note attached to a book."""

    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    book: Mapped[Book] = relationship(back_populates="entries")
    topics: Mapped[list[Topic]] = relationship(
        secondary=entry_topics, back_populates="entries"
    )
    people: Mapped[list[Person]] = relationship(
        secondary=entry_people, back_populates="entries"
    )
