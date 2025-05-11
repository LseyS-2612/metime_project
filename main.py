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

        # Temaya uygun renkleri ayarla
        if theme_name == "Purple & Gray":
            self.theme_colors = {
                "fg_color": "#6A0DAD",  # Mor
                "hover_color": "#8A2BE2"  # Daha açık mor
            }
        elif theme_name == "Orange & Gray":
            self.theme_colors = {
                "fg_color": "#FF9800",  # Turuncu
                "hover_color": "#F57C00"  # Daha koyu turuncu
            }

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


if __name__ == "__main__":
    app = MeditationApp()
    app.mainloop()
