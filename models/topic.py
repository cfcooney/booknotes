from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .junction import entry_topics

if TYPE_CHECKING:
    from .entry import Entry


class Topic(Base):
    """A topical tag that can be linked to notes."""

    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)

    entries: Mapped[list[Entry]] = relationship(
        secondary=entry_topics, back_populates="topics"
    )
