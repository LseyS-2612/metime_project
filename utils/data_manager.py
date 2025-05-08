import json
import os
import time
import random
import customtkinter as ctk


SETTINGS_PATH = "settings.json"
MEDITATION_DATA_PATH = "meditation_data.json"

def load_settings():
    """Ayarları settings.json dosyasından yükler."""
    base_dir = os.path.dirname(__file__)
    settings_path = os.path.join(base_dir, "..", "settings.json")
    try:
        with open(settings_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_settings(settings):
    """Ayarları settings.json dosyasına kaydeder."""
    base_dir = os.path.dirname(__file__)
    settings_path = os.path.join(base_dir, "..", "settings.json")
    with open(settings_path, "w", encoding="utf-8") as file:
        json.dump(settings, file, ensure_ascii=False, indent=4)

def load_meditation_data():
    if not os.path.exists(MEDITATION_DATA_PATH):
        return {"last_meditation_date": None, "streak": 0}
    with open(MEDITATION_DATA_PATH, "r") as f:
        return json.load(f)

def save_meditation_data(data):
    with open(MEDITATION_DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

def update_streak():
    data = load_meditation_data()
    today = time.strftime("%Y-%m-%d")
    last_date = data.get("last_meditation_date")

    if last_date == today:
        return data["streak"]

    if last_date:
        last_date_obj = time.strptime(last_date, "%Y-%m-%d")
        today_obj = time.strptime(today, "%Y-%m-%d")
        days_diff = (time.mktime(today_obj) - time.mktime(last_date_obj)) / (24 * 3600)

        if days_diff == 1:
            data["streak"] += 1
        else:
            data["streak"] = 1
    else:
        data["streak"] = 1

    data["last_meditation_date"] = today
    save_meditation_data(data)
    return data["streak"]

def load_audio_files():
        """Audio klasöründeki tüm alt klasörlerden ses dosyalarını yükler."""
        audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio"))
        audio_files = []
        try:
            for root, _, files in os.walk(audio_dir):  # Alt klasörleri de dolaş
                for file in files:
                    if file.lower().endswith((".mp3", ".wav")):  # Sadece ses dosyalarını seç
                        audio_files.append(os.path.join(root, file))
            if not audio_files:
                print("Hiçbir ses dosyası bulunamadı!")
            return audio_files
        except Exception as e:
            print(f"Ses dosyalarını yüklerken bir hata oluştu: {e}")
            return []
        

def start_daily_meditation(load_audio_files_func, show_screen_func, go_home_func):
    """Günlük meditasyon için rastgele bir ses dosyasını çalar ve meditasyon ekranını açar."""
    from screens.meditation_screen import MeditationScreen  # Geçici import

    audio_files = load_audio_files_func()
    if not audio_files:
        print("Hiçbir ses dosyası bulunamadı!")
        return

    # Rastgele bir ses dosyası seç
    random_audio = random.choice(audio_files)
    print(f"Çalınan ses dosyası: {random_audio}")  # Debug için

    # Ses dosyasını göreceli yola dönüştür
    base_audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio"))
    relative_audio_path = os.path.relpath(random_audio, base_audio_dir).replace("\\", "/")

    # Seans bilgisi oluştur
    seans = {
        "isim": "Günlük Meditasyon",
        "ses_dosyasi": relative_audio_path  # Göreceli dosya yolunu kullan
    }

    # Meditasyon ekranını aç
    show_screen_func(MeditationScreen, go_home_func, seans)

    
def create_menu_bar(self, parent):
        """Menü çubuğunu oluşturur."""
        menu_frame = ctk.CTkFrame(parent, height=60, fg_color="#343434")  # Menü çubuğu rengi
        menu_frame.pack(side="top", fill="x")

        # Menü çubuğundaki butonlar
        home_btn = ctk.CTkButton(
            menu_frame,
            text="🏠 Ana Sayfa",
            command=self.show_home,
            width=100,
            height=40,
            fg_color="#212121",
            hover_color="#312e33"
        )
        home_btn.place(x=10, y=10)

        settings_btn = ctk.CTkButton(
            menu_frame,
            text="⚙️ Ayarlar",
            command=self.show_settings,
            width=100,
            height=40,
            fg_color="#212121",
            hover_color="#312e33"
        )
        settings_btn.place(x=120, y=10)

        profile_btn = ctk.CTkButton(
            menu_frame,
            text="👤 Profil",
            command=self.show_profile,
            width=100,
            height=40,
            fg_color="#212121",
            hover_color="#312e33"
        )
        profile_btn.place(x=230, y=10)

        return menu_frame   