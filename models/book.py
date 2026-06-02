from __future__ import annotations

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

if TYPE_CHECKING:
    from .entry import Entry
    from .person import Person

# status values: to_read / reading / finished / reference


class Book(Base):
    """A book the user is reading, has read, or wants to read."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    fiction: Mapped[bool] = mapped_column(default=False)
    genre: Mapped[str | None] = mapped_column(String(120), nullable=True)
    year: Mapped[int | None] = mapped_column(nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="reading")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    finish_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_page: Mapped[int | None] = mapped_column(nullable=True)
    total_pages: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    entries: Mapped[list[Entry]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
    persons: Mapped[list[Person]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
