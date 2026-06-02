from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .associations import entry_people
from .base import Base

if TYPE_CHECKING:
    from .entry import Entry


class Person(Base):
    """A person or character referenced by notes."""

    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)

    entries: Mapped[list[Entry]] = relationship(
        secondary=entry_people, back_populates="people"
    )
