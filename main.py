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


SETTINGS_PATH = "settings.json"
MEDITATION_DATA_PATH = "meditation_data.json"

def save_settings(settings):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=4)

def load_meditation_data():
    """Meditasyon verilerini yükler."""
    if not os.path.exists(MEDITATION_DATA_PATH):
        return {"last_meditation_date": None, "streak": 0}
    with open(MEDITATION_DATA_PATH, "r") as f:
        return json.load(f)

def save_meditation_data(data):
    """Meditasyon verilerini kaydeder."""
    with open(MEDITATION_DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

def update_streak():
    """Streak'i günceller ve meditasyon verilerini kaydeder."""
    data = load_meditation_data()
    today = time.strftime("%Y-%m-%d")
    last_date = data.get("last_meditation_date")

    if last_date == today:
        # Bugün zaten meditasyon yapılmış
        return data["streak"]

        # Son meditasyon tarihi ile bugünü karşılaştır
        last_date_obj = time.strptime(last_date, "%Y-%m-%d")
        today_obj = time.strptime(today, "%Y-%m-%d")
        days_diff = (time.mktime(today_obj) - time.mktime(last_date_obj)) / (24 * 3600)

        if days_diff == 1:
            # Streak devam ediyor
            data["streak"] += 1
        else:
            # Streak sıfırlanıyor
            data["streak"] = 1
    else:
        # İlk meditasyon
        data["streak"] = 1

    # Güncel verileri kaydet
    data["last_meditation_date"] = today
    save_meditation_data(data)
    return data["streak"]

class MeditationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere ayarları
        self.title("Meditasyon Uygulaması")
        self.geometry("600x800")
        self.resizable(False, False)

        # Tema ayarı
        settings = load_settings()
        ctk.set_appearance_mode(settings.get("theme", "dark"))  # Tema ayarı
        ctk.set_default_color_theme("blue")  # Mavi tema

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
