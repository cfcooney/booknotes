from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from screens.home_screen import HomeScreen
from services.database import init_db


class BookNotesApp(App):
    def build(self) -> ScreenManager:
        init_db()
        manager = ScreenManager()
        manager.add_widget(HomeScreen(name="home"))
        return manager


if __name__ == "__main__":
    BookNotesApp().run()
