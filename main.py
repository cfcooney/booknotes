from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from models.database import init_db
from screens.add_book_screen import AddBookScreen
from screens.add_entry_screen import AddEntryScreen
from screens.book_screen import BookScreen
from screens.home_screen import HomeScreen


class BookNotesApp(App):
    def build(self) -> ScreenManager:
        init_db()
        manager = ScreenManager()
        manager.add_widget(HomeScreen(name="home"))
        manager.add_widget(AddBookScreen(name="add_book"))
        manager.add_widget(BookScreen(name="book"))
        manager.add_widget(AddEntryScreen(name="add_entry"))
        return manager


if __name__ == "__main__":
    BookNotesApp().run()
