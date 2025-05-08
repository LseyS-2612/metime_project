import customtkinter as ctk
import json
import os
import pygame
from screens.home_screen import HomeScreen
from screens.settings_screen import SettingsScreen
from screens.meditation_screen import MeditationScreen
from screens.profile_screen import ProfileScreen
from utils.data_manager import load_settings

class MeditationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere ayarları
        self.title("Meditasyon Uygulaması")
        self.geometry("600x800")
        self.resizable(False, False)

        # Tema ayarı
        settings = load_settings()
        if settings.get("theme") == "Purple & Gray":
            base_dir = os.path.dirname(__file__)
            theme_path = os.path.join(base_dir, "themes", "purple_gray_theme.json")
            ctk.set_default_color_theme(theme_path)
        elif settings.get("theme") == "Orange & Gray":
            base_dir = os.path.dirname(__file__)
            theme_path = os.path.join(base_dir, "themes", "orange_gray_theme.json")
            ctk.set_default_color_theme(theme_path)

        # Sayfa yerleştirme
        self.current_frame = None
        self.show_home()  # İlk açılışta ana sayfayı göster

    def clear_frame(self):
        if self.current_frame:
            if isinstance(self.current_frame, MeditationScreen):
                self.current_frame.running = False  # Timer'ı durdur
            self.current_frame.destroy()

    def show_home(self):
        self.clear_frame()
        self.current_frame = HomeScreen(self, self.show_meditation, self.show_settings, self.show_profile)
        self.current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_meditation(self, seans):
        self.clear_frame()
        self.current_frame = MeditationScreen(self, self.show_home, seans)
        self.current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_profile(self):
        """Profil ekranını gösterir."""
        self.clear_frame()
        self.current_frame = ProfileScreen(self, self.show_home)
        self.current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_settings(self):
        """Ayarlar ekranını gösterir."""
        self.clear_frame()
        self.current_frame = SettingsScreen(self, self.show_home)
        self.current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)


if __name__ == "__main__":
    app = MeditationApp()
    app.mainloop()
