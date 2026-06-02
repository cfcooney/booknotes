from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .junction import entry_people

if TYPE_CHECKING:
    from .book import Book
    from .entry import Entry


class Person(Base):
    """A character or person referenced in a book's notes."""

    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    book: Mapped[Book] = relationship(back_populates="persons")
    entries: Mapped[list[Entry]] = relationship(
        secondary=entry_people, back_populates="people"
    )
