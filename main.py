import customtkinter as ctk
import json
import os
import pygame
from screens.home_screen import HomeScreen
from screens.settings_screen import SettingsScreen
from screens.meditation_screen import MeditationScreen
from screens.profile_screen import ProfileScreen
from utils.data_manager import load_settings
from screens.show_courses_screen import CoursesScreen
from screens.sessions_screen import SessionsScreen
from screens.challenges_screen import ChallengesScreen
from screens.timer_screen import TimerScreen
from screens.countdown_screen import CountdownScreen
from screens.emergency_screen import EmergencyScreen
from screens.favorites_screen import FavoritesScreen
from screens.downloads_screen import DownloadsScreen

class MeditationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        pygame.mixer.init()  # Uygulama başlatıldığında bir kez başlat
        self.json_cache = {}  # JSON dosyalarını önbelleğe almak için bir sözlük
        self.load_all_json_files()  # JSON dosyalarını önceden yükle

        self.audio_cache = {}  # Ses dosyalarını önbelleğe almak için bir sözlük
        self.preload_audio_files()

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
        """Tema ayarlarını uygular."""
        # Tema dosyası zaten yüklüyse tekrar yükleme
        if hasattr(self, 'current_theme') and self.current_theme == theme_name:
            return
            
        base_dir = os.path.dirname(__file__)
        theme_file = f"{theme_name.lower().replace(' & ', '_')}_theme.json"
        theme_path = os.path.join(base_dir, "themes", theme_file)
        
        if os.path.exists(theme_path):
            ctk.set_default_color_theme(theme_path)
            self.current_theme = theme_name
            
            # Temaya uygun renkleri ayarla
            theme_colors = {
                "Purple & Gray": {
                    "fg_color": "#6A0DAD",
                    "hover_color": "#8A2BE2"
                },
                "Orange & Gray": {
                    "fg_color": "#FF9800",
                    "hover_color": "#F57C00"
                }
            }
            
            self.theme_colors = theme_colors.get(theme_name, theme_colors["Purple & Gray"])

    def clear_frame(self):
        """Eski çerçeveyi temizler ve bellek yönetimini iyileştirir."""
        if self.current_frame:
            # Çerçeve temizlenmeden önce garbage collection'a yardımcı olmak için bileşenleri serbest bırak
            for widget in self.current_frame.winfo_children():
                widget.destroy()
            self.current_frame.destroy()
            self.current_frame = None

    def show_screen(self, screen_class, *args):
        """Ekranları gösterir ve önceki ekranı temizler."""
        # Pygame mixer'ı kullanımda değilse temizle
        if hasattr(self, 'current_frame') and self.current_frame and not isinstance(self.current_frame, MeditationScreen):
            pygame.mixer.stop()  # Tüm ses kanallarını temizle

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

    def show_favorites(self):
        """Favoriler ekranını açar."""
        self.show_screen(MeditationScreen, self.show_home, {"ses_dosyasi": "favorites"})
        
    def show_courses(self):
        """Kurslar ekranını açar."""
        self.show_screen(CoursesScreen, self.show_home)

    def show_sessions(self):
        """Seanslar ekranını açar."""
        self.show_screen(SessionsScreen, self.show_home)

    def show_challenges(self):
        """Zorluklar ekranını açar."""
        self.show_screen(ChallengesScreen, self.show_home)

    def show_timer_screen(self):
        """Zamanlayıcı ekranını gösterir."""
        self.show_screen(TimerScreen, self.show_home)

    def load_all_json_files(self):
        """Tüm JSON dosyalarını önceden yükler."""
        base_dir = os.path.dirname(__file__)
        json_files = ["favorites.json", "background_sounds.json", "courses.json"]
        
        for json_file in json_files:
            file_path = os.path.join(base_dir, json_file)
            try:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as file:
                        self.json_cache[json_file] = json.load(file)
                else:
                    # Dosya yoksa varsayılan boş yapı oluştur
                    self.json_cache[json_file] = {}
            except Exception as e:
                print(f"{json_file} yüklenirken hata: {e}")
                self.json_cache[json_file] = {}

    def get_cached_json(self, file_name):
        """Önbellekten JSON dosyasını alır."""
        return self.json_cache.get(file_name, {})

    def preload_audio_files(self):
        """Ses dosyalarını önceden yükler."""
        audio_dir = os.path.join(os.path.dirname(__file__), "audio")
        # Sadece doğrudan audio klasöründeki dosyaları yükle, alt klasörleri kontrol et
        for item in os.listdir(audio_dir):
            file_path = os.path.join(audio_dir, item)
            if os.path.isfile(file_path) and item.endswith(('.mp3', '.wav', '.ogg')):
                try:
                    self.audio_cache[item] = pygame.mixer.Sound(file_path)
                except:
                    pass  # Yüklenemezse sessizce devam et

    def get_cached_audio(self, file_name):
        """Önbellekten ses dosyasını alır."""
        if file_name in self.audio_cache:
            return self.audio_cache[file_name]
        
        # Önbellekte yoksa dosyadan yüklemeyi dene
        try:
            audio_dir = os.path.join(os.path.dirname(__file__), "audio")
            file_path = os.path.join(audio_dir, file_name)
            if os.path.isfile(file_path):
                sound = pygame.mixer.Sound(file_path)
                self.audio_cache[file_name] = sound  # Önbelleğe ekle
                return sound
        except Exception as e:
            print(f"Ses dosyası yüklenirken hata: {e}")
        
        return None


if __name__ == "__main__":
    # Uygulama başlatılmadan önce sistem ayarlarını optimize et
    import sys
    
    # Windows'ta DPI farkındalığını etkinleştir
    if sys.platform.startswith('win'):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    
    # Ana uygulama başlat
    app = MeditationApp()
    app.mainloop()
