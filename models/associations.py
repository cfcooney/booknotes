"""Re-exports junction tables from models.junction for backward compatibility."""

from .junction import entry_people, entry_topics

__all__ = ["entry_topics", "entry_people"]
