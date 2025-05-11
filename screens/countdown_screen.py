import customtkinter as ctk
import os
import json
import pygame
import threading
from screens.base_screen import BaseScreen

class CountdownScreen(BaseScreen):
    def __init__(self, master, go_back, minutes):
        super().__init__(master)
        
        # Ses kontrolü için değişkenler
        self.selected_audio_path = None  # Seçilen ses dosyasının yolu
        self.audio_playing = False  # Ses oynatma durumu (Başlangıçta False)

        # Arka plan resmini yeniden ekle
        if hasattr(self, "bg_image"):
            bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
            bg_label.lower()  # Arka planı en alta yerleştir

        # Geri dönüş butonu
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",
            width=40,
            height=40,
            command=go_back,  # Ana ekrana geri dönmek için
            fg_color=self.master.theme_colors["fg_color"],  # Temaya uygun renk
            hover_color=self.master.theme_colors["hover_color"]  # Temaya uygun hover rengi
        )
        back_btn.place(x=10, y=10)

        # Geri sayım etiketi
        self.countdown_label = ctk.CTkLabel(
            self,
            text="",
            font=("Helvetica", 48, "bold"),
            text_color="#FFFFFF"
        )
        self.countdown_label.place(relx=0.5, rely=0.4, anchor="center")

        # Duraklat/Devam Et butonu
        self.paused = False  # Duraklatma durumu
        self.pause_btn = ctk.CTkButton(
            self,
            text="Duraklat",
            width=100,
            height=40,
            command=self.toggle_pause,
            fg_color=self.master.theme_colors["fg_color"],  # Temaya uygun renk
            hover_color=self.master.theme_colors["hover_color"],  # Temaya uygun hover rengi
            corner_radius=20
        )
        self.pause_btn.place(relx=0.5, rely=0.6, anchor="center")
        
        # Ses kontrol paneli
        self.audio_control_panel = ctk.CTkFrame(self, fg_color="#2E2E2E", corner_radius=10, height=30)
        self.audio_control_panel.pack(side="bottom", pady=20, fill="x", padx=40)
        
        # Ses dosyalarını JSON'dan yükle
        self.load_background_sounds()
        
        # Ses dosyası seçimi için menü
        self.audio_selection_menu = ctk.CTkOptionMenu(
            self.audio_control_panel,
            values=self.background_sounds_names,
            command=self.select_audio_file
        )
        self.audio_selection_menu.set("Ses Dosyası Seç")
        self.audio_selection_menu.grid(row=0, column=0, padx=10, pady=10)
        
        # Başlat/Durdur butonu
        self.audio_play_pause_btn = ctk.CTkButton(
            self.audio_control_panel,
            text="▶️",  # Başlat ikonu
            command=self.toggle_audio_playback,
            width=50,
            height=50
        )
        self.audio_play_pause_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # Ses seviyesi ayarlama slider'ı
        self.audio_volume_slider = ctk.CTkSlider(
            self.audio_control_panel,
            from_=0,
            to=1,
            number_of_steps=30,
            command=self.change_audio_volume
        )
        self.audio_volume_slider.set(0.5)  # Varsayılan orta seviye
        self.audio_volume_slider.grid(row=0, column=2, padx=10, pady=10)
        
        # Timer ekranından gelen ses durumunu kontrol et ve uygula
        if hasattr(self.master, 'audio_state') and self.master.audio_state:
            audio_state = self.master.audio_state
            self.selected_audio_path = audio_state.get("path")
            
            # Doğru ses dosyasını seç
            for sound in self.background_sounds:
                if os.path.basename(self.selected_audio_path) == sound["file"]:
                    self.audio_selection_menu.set(sound["name"])
                    break
            
            # Ses durumunu ayarla
            if audio_state.get("playing"):
                sound = pygame.mixer.Sound(self.selected_audio_path)
                pygame.mixer.Channel(2).play(sound, loops=-1)
                self.audio_play_pause_btn.configure(text="⏸️")
                self.audio_playing = True
                self.audio_volume_slider.set(audio_state.get("volume", 0.5))
                pygame.mixer.Channel(2).set_volume(audio_state.get("volume", 0.5))

        # Geri sayımı başlat
        self.remaining_seconds = minutes * 60
        self.update_countdown()

    def toggle_pause(self):
        """Geri sayımı duraklatır veya devam ettirir."""
        if self.paused:
            self.paused = False
            self.pause_btn.configure(text="Duraklat")
            self.update_countdown()  # Geri sayımı yalnızca duraklatma durumundan çıkıldığında başlat
        else:
            self.paused = True
            self.pause_btn.configure(text="Devam Et")

    def update_countdown(self):
        """Geri sayımı günceller."""
        if not self.paused:  # Eğer duraklatılmamışsa
            if self.remaining_seconds > 0:
                minutes = self.remaining_seconds // 60
                seconds = self.remaining_seconds % 60
                self.countdown_label.configure(text=f"{minutes:02}:{seconds:02}")
                self.remaining_seconds -= 1
                self.after(1000, self.update_countdown)  # 1 saniye sonra tekrar çağır
            else:
                self.countdown_label.configure(text="Süre Doldu!")
                
    def load_background_sounds(self):
        """Arka plan seslerini JSON dosyasından yükler."""
        self.background_sounds = []
        self.background_sounds_names = []

        sounds_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "background_sounds.json"))
        if os.path.exists(sounds_file):
            with open(sounds_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.background_sounds = data.get("sounds", [])
                self.background_sounds_names = [sound["name"] for sound in self.background_sounds]
    
    def select_audio_file(self, selection):
        """Seçilen ses dosyasını ayarlar."""
        for sound in self.background_sounds:
            if sound["name"] == selection:
                audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "Arka Plan Sesleri"))
                self.selected_audio_path = os.path.join(audio_dir, sound["file"])
                break

    def toggle_audio_playback(self):
        """Seçilen ses dosyasını başlatır veya durdurur."""
        if not self.selected_audio_path or not os.path.exists(self.selected_audio_path):
            return

        if self.audio_playing:
            pygame.mixer.Channel(2).stop()  # Ses dosyasını durdur
            self.audio_play_pause_btn.configure(text="▶️")  # Başlat ikonuna geri dön
            self.audio_playing = False
        else:
            sound = pygame.mixer.Sound(self.selected_audio_path)
            pygame.mixer.Channel(2).play(sound, loops=-1)  # loops=-1 sonsuz döngü anlamına gelir
            self.audio_play_pause_btn.configure(text="⏸️")  # Durdur ikonuna geç
            self.audio_playing = True

    def change_audio_volume(self, value):
        """Ses dosyasının ses seviyesini değiştirir."""
        pygame.mixer.Channel(2).set_volume(float(value))