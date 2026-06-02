from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from screens.home_screen import HomeScreen


class BookNotesApp(App):
    def build(self) -> ScreenManager:
        Builder.load_file("booknotes.kv")
        manager = ScreenManager()
        manager.add_widget(HomeScreen(name="home"))
        return manager


if __name__ == "__main__":
    BookNotesApp().run()
