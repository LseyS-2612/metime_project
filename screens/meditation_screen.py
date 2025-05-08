import os
import time
import threading
import json
import customtkinter as ctk
import pygame
from screens.home_screen import HomeScreen
from screens.settings_screen import SettingsScreen
from utils.data_manager import load_settings, save_settings, load_settings, save_meditation_data, update_streak


class MeditationScreen(ctk.CTkFrame):
    def __init__(self, master, go_home, seans):
        super().__init__(master)
        self.master = master
        self.go_home = go_home
        self.running = False
        self.paused = False
        self.audio_path = None
        self.hide_slider_job = None

        # Varsayılan süreyi başlat
        self.duration = 0  # Varsayılan olarak 0 saniye
        self.remaining = 0  # Geri sayım için süre

        # Ses motorunu başlat
        pygame.mixer.init()

        # Ses dosyasını al ve süresini belirle
        self.audio_path = self.get_audio_path(seans)
        if self.audio_path:
            self.remaining = self.duration  # Süreyi geri sayım için ayarla

        # Başlık
        ctk.CTkLabel(self, text=f"{self.duration // 60} Dakikalık Meditasyon", font=("Arial", 22, "bold")).pack(pady=20)

        # Sayaç
        self.timer_label = ctk.CTkLabel(self, text=self.format_time(self.remaining), font=("Arial", 40))
        self.timer_label.pack(pady=10)

        # Başlat/Duraklat butonu
        self.start_pause_btn = ctk.CTkButton(self, text="▶️ Başlat", command=self.start_or_pause_meditation)
        self.start_pause_btn.pack(pady=10)

        # Geri butonu
        self.back_btn = ctk.CTkButton(self, text="⬅️", command=self.stop_and_return, width=40, height=40, fg_color="#212121", hover_color="#312e33")
        self.back_btn.pack(pady=10)
        self.back_btn.place(x=5, y=5)  # Sol üst köşeye yerleştir

        # Ses simgesi
        self.volume_icon = ctk.CTkLabel(self, text="🔊", font=("Arial", 24))
        self.volume_icon.place(x=550, y=10)  # Sol tarafa yerleştir

        # Ses seviyesi slider'ı için çerçeve
        self.volume_frame = ctk.CTkFrame(self, width=50, height=200)

        # Ses seviyesi slider'ı (dikey)
        self.volume_slider = ctk.CTkSlider(
            self.volume_frame,
            from_=0,
            to=1,
            number_of_steps=30,
            orientation="vertical",
            command=self.change_volume
        )
        self.volume_slider.set(0.5)  # Varsayılan orta seviye
        self.volume_slider.pack(pady=10)
        self.volume_frame.place(x=555, y=35)  # Ses simgesinin hemen altına yerleştir

        # Slider başlangıçta gizli
        self.volume_frame.place_forget()

        # Fare olayları
        self.volume_icon.bind("<Enter>", self.show_volume_slider)
        self.volume_icon.bind("<Leave>", self.hide_volume_slider_delayed)
        self.volume_frame.bind("<Enter>", self.show_volume_slider)
        self.volume_frame.bind("<Leave>", self.hide_volume_slider_delayed)
        self.volume_slider.bind("<Enter>", self.cancel_hide_slider)
        self.volume_slider.bind("<Leave>", self.hide_volume_slider_delayed)

        # Başlangıçta sesi ayarla
        pygame.mixer.music.set_volume(0.5)

    def show_volume_slider(self, event=None):
        """Slider'ı göster."""
        if self.hide_slider_job:
            self.after_cancel(self.hide_slider_job)  # Gizleme işlemini iptal et
            self.hide_slider_job = None
        self.volume_frame.place(x=555, y=35)  # Ses simgesinin hemen altına yerleştir

    def hide_volume_slider_delayed(self, event=None):
        """Slider'ı gecikmeli olarak gizle."""
        self.hide_slider_job = self.after(300, self.hide_volume_slider)  # 300ms gecikme

    def hide_volume_slider(self, event=None):
        """Slider'ı gizle."""
        self.volume_frame.place_forget()
        self.hide_slider_job = None

    def cancel_hide_slider(self, event=None):
        """Slider'ın gizlenmesini iptal et."""
        if self.hide_slider_job:
            self.after_cancel(self.hide_slider_job)
            self.hide_slider_job = None

    def change_volume(self, value):
        """Ses seviyesini değiştir."""
        pygame.mixer.music.set_volume(float(value))

    def start_or_pause_meditation(self):
        if not self.running:
            # Meditasyonu başlat
            self.running = True
            self.paused = False
            self.start_pause_btn.configure(text="⏸️ Duraklat")

            # Eğer müzik çalmıyorsa başlat
            if not pygame.mixer.music.get_busy():
                if self.audio_path:
                    pygame.mixer.music.load(self.audio_path)
                    pygame.mixer.music.play(start=self.duration - self.remaining)  # Kaldığı yerden başlat
                else:
                    ctk.CTkLabel(self, text="⚠️ Ses dosyası bulunamadı!", font=("Arial", 14, "bold"), fg_color="red").pack(pady=10)
                    return
            else:
                pygame.mixer.music.unpause()  # Eğer duraklatılmışsa devam ettir

            # Timer thread'i başlat
            threading.Thread(target=self.run_timer, daemon=True).start()
        elif self.paused:
            # Duraklatıldıysa devam et
            self.paused = False
            self.running = True
            self.start_pause_btn.configure(text="⏸️ Duraklat")
            pygame.mixer.music.unpause()  # Müziği devam ettir
        else:
            # Devam ediyorsa duraklat
            self.paused = True
            self.running = False
            self.start_pause_btn.configure(text="▶️ Devam Et")
            pygame.mixer.music.pause()  # Müziği duraklat

    def cleanup(self):
        self.running = False  # Timer'ı durdur
        pygame.mixer.music.stop()  # Müzik çalmayı durdur

    def pause_timer(self):
        # Timer'ı duraklat
        self.running = False

    def resume_timer(self):
        # Timer'ı devam ettir
        self.running = True
        threading.Thread(target=self.run_timer, daemon=True).start()

    def run_timer(self):
        while self.running and self.remaining > 0:
            time.sleep(1)
            if self.paused:  # Timer duraklatıldıysa bekle
                continue
            self.remaining -= 1

            # Widget'ın hala mevcut olup olmadığını kontrol edin
            if not self.winfo_exists():
                break

            # Timer'ı güncelle
            self.timer_label.configure(text=self.format_time(self.remaining))

        # Timer bittiğinde
        if self.remaining <= 0 and self.running:
            self.running = False
            self.start_pause_btn.configure(text="▶️ Başlat")

            # Timer bittiğinde
            if self.remaining <= 0 and self.running:
                self.running = False
                self.start_pause_btn.configure(text="▶️ Başlat")

    def get_audio_path(self, seans):
        """Seçilen seansın ses dosyasını döndürür ve süresini hesaplar."""
        audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio"))
        audio_path = os.path.join(audio_dir, seans["ses_dosyasi"])
        print(f"Ses dosyası yolu: {audio_path}")  # Debug için
        if os.path.exists(audio_path):
            self.duration = self.get_audio_duration(audio_path)  # Süreyi otomatik olarak al
            return audio_path
        print("Ses dosyası bulunamadı!")  # Debug için
        return None  # Ses dosyası bulunamazsa None döndür

    def get_audio_duration(self, audio_path):
        """Ses dosyasının süresini saniye cinsinden döndürür."""
        if not audio_path or not os.path.exists(audio_path):
            return 0
        pygame.mixer.init()
        sound = pygame.mixer.Sound(audio_path)
        return int(sound.get_length())  # Süreyi saniye cinsinden döndür

    def format_time(self, seconds):
        """Saniyeyi dakika:saniye formatına dönüştürür."""
        m, s = divmod(seconds, 60)
        return f"{int(m):02}:{int(s):02}"

    def end_session(self):
        self.running = False
        pygame.mixer.music.stop()
        self.timer_label.configure(text="⏳ Süre Bitti")

    def stop_and_return(self):
        """Meditasyon ekranını kapat ve ana ekrana dön."""
        self.running = False  # Timer'ı durdur
        pygame.mixer.music.stop()  # Müzik çalmayı durdur
        self.go_home()
