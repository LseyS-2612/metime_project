import customtkinter as ctk
import json
import os
import pygame
import time
import threading
from screens.home_screen import HomeScreen
from screens.settings_screen import SettingsScreen
from screens.meditation_screen import MeditationScreen  # Eğer meditasyon ekranı varsa
from utils.data_manager import load_settings  # Ayarları yüklemek için

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
            ctk.set_default_color_theme("C:/Users/klcan/metime_project/themes/purple_gray_theme.json")
        elif settings.get("theme") == "Orange & Gray":
            ctk.set_default_color_theme("C:/Users/klcan/metime_project/themes/orange_gray_theme.json")

        # Sayfa yerleştirme
        self.current_frame = None
        self.show_home()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_home(self):
        self.clear_frame()
        self.current_frame = HomeScreen(self, self.show_meditation, self.show_settings)
        self.current_frame.pack(fill="both", expand=True)

    def show_meditation(self, selected_minutes=5):
        self.clear_frame()
        self.current_frame = MeditationScreen(self, self.show_home, selected_minutes)
        self.current_frame.pack(fill="both", expand=True)

    def show_settings(self):
        self.clear_frame()
        self.current_frame = SettingsScreen(self, self.show_home)
        self.current_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = MeditationApp()
    app.mainloop()
