from sqlalchemy import Column, ForeignKey, Table

from .database import Base

entry_topics = Table(
    "entry_topics",
    Base.metadata,
    Column("entry_id", ForeignKey("entries.id"), primary_key=True),
    Column("topic_id", ForeignKey("topics.id"), primary_key=True),
)

entry_people = Table(
    "entry_people",
    Base.metadata,
    Column("entry_id", ForeignKey("entries.id"), primary_key=True),
    Column("person_id", ForeignKey("people.id"), primary_key=True),
)
