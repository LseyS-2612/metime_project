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
        pygame.mixer.init()  # Uygulama başlatıldığında bir kez başlat
        # Pencere ayarları  
        self.title("MeTime")
        self.geometry("600x800")
        self.resizable(False, False)

        # Tema ayarı
        settings = load_settings()
        if settings.get("theme") == "Purple & Gray":
            self.apply_theme(settings.get("theme", "Purple & Gray"))  # Varsayılan tema
        elif settings.get("theme") == "Orange & Gray":
            self.apply_theme(settings.get("theme", "Orange & Gray"))  # Varsayılan tema
        # Sayfa yerleştirme
        self.current_frame = None
        self.show_home()  # İlk açılışta ana sayfayı göster

    def apply_theme(self, theme_name):
        base_dir = os.path.dirname(__file__)
        theme_file = f"{theme_name.lower().replace(' & ', '_')}_theme.json"
        theme_path = os.path.join(base_dir, "themes", theme_file)
        ctk.set_default_color_theme(theme_path)


    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_screen(self, screen_class, *args):
        self.clear_frame()
        self.current_frame = screen_class(self, *args)
        self.current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)


    def show_home(self):
        self.show_screen(HomeScreen, self.show_meditation, self.show_settings, self.show_profile)

    def show_meditation(self, seans):
        self.show_screen(MeditationScreen, self.show_home, seans)

    def show_profile(self):
        self.show_screen(ProfileScreen, self.show_home)

    def show_settings(self):
        self.show_screen(SettingsScreen, self.show_home)


if __name__ == "__main__":
    app = MeditationApp()
    app.mainloop()
