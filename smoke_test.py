from models import Book, Entry, Person, Topic
from services.database import get_session, init_db

# create tables (safe to call repeatedly — skips existing tables)
init_db()

session = get_session()

# --- seed data ---
book = Book(title="Meditations", author="Marcus Aurelius")
topic = Topic(name="stoicism")
person = Person(name="Epictetus")
session.add_all([book, topic, person])

entry = Entry(
    title="On impermanence", content="Loss is nothing else but change.", book=book
)
entry.topics.append(topic)
entry.people.append(person)
session.add(entry)
session.commit()

# --- read back and verify ---
fetched = session.get(Entry, entry.id)

print(f"Entry:   {fetched.title}")
print(f"Book:    {fetched.book.title}")
print(f"Topics:  {[t.name for t in fetched.topics]}")
print(f"People:  {[p.name for p in fetched.people]}")

# verify the reverse side of the join
print(f"Topic's entries: {[e.title for e in topic.entries]}")
print(f"Person's entries: {[e.title for e in person.entries]}")

session.close()
print("\nSmoke test passed.")
