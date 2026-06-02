from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .junction import entry_people, entry_topics

if TYPE_CHECKING:
    from .book import Book
    from .person import Person
    from .topic import Topic

# type values: quote / note / fact
# importance values: 1 (low) / 2 (medium) / 3 (high)


class Entry(Base):
    """A single note, quote, or fact captured while reading a book."""

    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    type: Mapped[str] = mapped_column(String(20))
    text: Mapped[str] = mapped_column(Text)
    page: Mapped[int | None] = mapped_column(nullable=True)
    key_takeaway: Mapped[bool] = mapped_column(default=False)
    importance: Mapped[int | None] = mapped_column(nullable=True)
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
