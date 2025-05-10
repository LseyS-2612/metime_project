import os
import time
import threading
import json
import customtkinter as ctk
import pygame
import tkinter.messagebox as messagebox  # Mesaj kutusu göstermek için
import re  # Büyük harflerle başlayan kelimeleri ayıklamak için
from screens.home_screen import HomeScreen
from screens.settings_screen import SettingsScreen
from screens.base_screen import BaseScreen
from utils.data_manager import load_settings, save_settings, load_settings, save_meditation_data, update_streak


class MeditationScreen(BaseScreen):
    def __init__(self, master, go_home, seans):
        super().__init__(master)

        self.master = master
        self.go_home = go_home
        self.running = False
        self.paused = False
        self.audio_path = None
        self.hide_slider_job = None

        if seans["ses_dosyasi"] == "favorites":
            # Favoriler ekranı
            self.show_favorites_screen()
        else:
            # Günlük meditasyon ekranı
            self.setup_meditation_screen(seans)

    def setup_meditation_screen(self, seans):
        """Meditasyon ekranını hazırlar."""

        # Varsayılan süreyi başlat
        self.duration = 0  # Varsayılan olarak 0 saniye
        self.remaining = 0  # Geri sayım için süre

        # Ses motorunu başlat
        pygame.mixer.init()

        # Ses dosyasını al ve süresini belirle
        self.audio_path = self.get_audio_path(seans)
        if self.audio_path:
            self.remaining = self.duration  # Süreyi geri sayım için ayarla

        # 1. Dosyanın adı (klasör adı)
        audio_folder_name = os.path.basename(os.path.dirname(self.audio_path)) if self.audio_path else "Bilinmiyor"
        ctk.CTkLabel(self, text=f"{audio_folder_name}", font=("Arial", 22, "bold")).pack(pady=10)

        # 2. Ses dosyasının adı
        audio_file_name = self.get_audio_name_from_courses(seans["ses_dosyasi"])
        ctk.CTkLabel(self, text=f"{audio_file_name}", font=("Arial", 18)).pack(pady=10)

        # 3. Timer (Sayaç)
        self.timer_label = ctk.CTkLabel(self, text=self.format_time(self.remaining), font=("Arial", 40))
        self.timer_label.pack(pady=10)
        # 4. Slider (Ses İleri/Geri Sarma)
        slider_frame = ctk.CTkFrame(self)  # Slider ve butonlar için bir çerçeve oluştur
        slider_frame.pack(pady=10)

        # 10 saniye geri sarma butonu
        self.rewind_btn = ctk.CTkButton(slider_frame, text="⏪ 10s", command=self.rewind_audio, width=60)
        self.rewind_btn.pack(side="left", padx=5)

        # Slider
        self.seek_slider = ctk.CTkSlider(
            slider_frame,
            from_=0,
            to=self.duration,
            command=self.seek_audio,
            number_of_steps=self.duration
        )
        self.seek_slider.set(0)  # Varsayılan başlangıç değeri
        self.seek_slider.pack(side="left", fill="x", expand=True, padx=5)

        # 10 saniye ileri sarma butonu
        self.forward_btn = ctk.CTkButton(slider_frame, text="10s ⏩", command=self.forward_audio, width=60)
        self.forward_btn.pack(side="left", padx=5)

        # 5. Başlat/Duraklat butonu
        self.start_pause_btn = ctk.CTkButton(self, text="▶️ Başlat", command=self.start_or_pause_meditation)
        self.start_pause_btn.pack(pady=10)

        # Favorilere Ekle/Çıkar butonu
        self.add_to_favorites_btn = ctk.CTkButton(
            self,
            text="⭐ Favorilere Ekle",
            command=lambda: self.add_to_favorites(seans),
            width=200,
            height=40
        )
        self.add_to_favorites_btn.pack(pady=10)  # Başlat butonunun altına ekleniyor

        # Geri butonu
        self.back_btn = ctk.CTkButton(self, text="⬅️", command=self.stop_and_return, width=40, height=40, fg_color="#212121", hover_color="#312e33")
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

    def show_favorites_screen(self):
        """Favoriler ekranını gösterir ve dosya isimlerini listeler."""
        favorites_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "favorites.json"))
        if not os.path.exists(favorites_file):
            ctk.CTkLabel(self, text="Henüz favorilere eklenmiş bir ses dosyası yok.", font=("Arial", 14)).pack(pady=20)
            return

        with open(favorites_file, "r", encoding="utf-8") as file:
            favorites = json.load(file)

        ctk.CTkLabel(self, text="Favoriler", font=("Arial", 22, "bold")).pack(pady=10)

        for audio_file in favorites:
            # Dosya adını uzantısız olarak al ve büyük harflerle başlayan kelimeleri ayıkla
            file_name = os.path.splitext(audio_file)[0]
            capitalized_words = " ".join(re.findall(r'\b[A-Z][a-z]*\b', file_name))

            # Dosya adını göster
            audio_label = ctk.CTkLabel(self, text=capitalized_words, font=("Arial", 14))
            audio_label.pack(pady=5)

            # Oynat butonu
            play_button = ctk.CTkButton(
                self,
                text="▶️ Oynat",
                command=lambda file=audio_file: self.play_favorite_audio(file),
                width=100,
                height=30
            )
            play_button.pack(pady=5)

            # Favorilerden çıkar butonu (soft renkler)
            remove_button = ctk.CTkButton(
                self,
                text="❌ Favorilerden Çıkar",
                command=lambda file=audio_file: self.remove_from_favorites(file),
                width=150,
                height=30,
                fg_color="#FFC1C1",  # Soft pembe
                hover_color="#FFB3B3"  # Daha koyu soft pembe
            )
            remove_button.pack(pady=5)

        # Geri butonu
        self.back_btn = ctk.CTkButton(self, text="⬅️", command=self.stop_and_return, width=40, height=40, fg_color="#212121", hover_color="#312e33")
        self.back_btn.place(x=5, y=5)

    def remove_from_favorites(self, audio_file):
        """Favorilerden bir ses dosyasını çıkarır."""
        favorites_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "favorites.json"))
        if not os.path.exists(favorites_file):
            messagebox.showinfo("Favoriler", "Favoriler dosyası bulunamadı.")
            return

        with open(favorites_file, "r", encoding="utf-8") as file:
            favorites = json.load(file)

        if audio_file in favorites:
            favorites.remove(audio_file)
            with open(favorites_file, "w", encoding="utf-8") as file:
                json.dump(favorites, file, ensure_ascii=False, indent=4)
            messagebox.showinfo("Favoriler", f"{audio_file} favorilerden çıkarıldı!")
            self.clear_frame()
            self.show_favorites_screen()  # Ekranı güncelle
        else:
            messagebox.showinfo("Favoriler", f"{audio_file} favorilerde bulunamadı.")

    def play_favorite_audio(self, audio_file):
        """Favorilerdeki bir ses dosyasını çalar."""
        audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio"))
        audio_path = os.path.join(audio_dir, audio_file)

        if os.path.exists(audio_path):
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            print(f"{audio_file} çalınıyor...")
        else:
            print(f"Ses dosyası bulunamadı: {audio_path}")

    def get_audio_name_from_courses(self, audio_path):
        """Ses dosyasına karşılık gelen ismi courses.json dosyasından alır."""
        course_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "courses.json"))
        audio_file_name = "Bilinmiyor"  # Varsayılan değer

        if os.path.exists(course_file_path):
            with open(course_file_path, "r", encoding="utf-8") as course_file:
                course_data = json.load(course_file)
                for bölüm in course_data.get("Bölümler", []):  # "Bölümler" anahtarını kullanıyoruz
                    for seans in bölüm.get("seanslar", []):  # Her bölümdeki "seanslar"ı dolaşıyoruz
                        if seans.get("ses_dosyasi") == audio_path.replace("\\", "/"):  # Yol eşleşmesini kontrol et
                            audio_file_name = seans.get("isim", "Bilinmiyor")  # "isim" anahtarını al
                            return audio_file_name

        return audio_file_name

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

    def seek_audio(self, value):
        """Slider hareket ettirildiğinde sesi ve timer'ı günceller."""
        if self.audio_path and pygame.mixer.music.get_busy():
            # Sesi belirtilen saniyeye sar
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=float(value))

            # Timer'ı güncelle
            self.remaining = self.duration - int(value)
            self.timer_label.configure(text=self.format_time(self.remaining))

    def start_or_pause_meditation(self):
        if not self.running:
            # Eğer meditasyon sıfırlanmışsa (bittiği için)
            if self.remaining == 0:
                self.remaining = self.duration  # Süreyi baştan başlat
                self.seek_slider.set(0)  # Slider'ı başa al
                self.timer_label.configure(text=self.format_time(self.remaining))  # Timer'ı güncelle

            # Meditasyonu başlat
            self.running = True
            self.paused = False
            self.start_pause_btn.configure(text="⏸️ Duraklat")

            # Eğer müzik çalmıyorsa başlat
            if not pygame.mixer.music.get_busy():
                if self.audio_path:
                    pygame.mixer.music.load(self.audio_path)
                    pygame.mixer.music.play()
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

            # Slider'ı güncelle
            self.seek_slider.set(self.duration - self.remaining)

        # Timer bittiğinde
        if self.remaining <= 0 and self.running:
            self.running = False
            self.start_pause_btn.configure(text="▶️ Başlat")
            self.end_session()  # Meditasyon bittiğinde sıfırlama işlemini çağır

    def end_session(self):
        """Meditasyon bittiğinde timer ve slider'ı sıfırla."""
        self.running = False
        pygame.mixer.music.stop()  # Müziği durdur
        self.remaining = 0  # Timer'ı sıfırla
        self.timer_label.configure(text=self.format_time(self.remaining))  # Timer'ı güncelle
        self.seek_slider.set(0)  # Slider'ı sıfırla
        self.start_pause_btn.configure(text="▶️ Başlat")  # Butonu başlat durumuna getir

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

    def rewind_audio(self):
        """Sesi 10 saniye geri sar."""
        if self.audio_path and pygame.mixer.music.get_busy():
            new_time = max(0, self.seek_slider.get() - 10)  # 10 saniye geri sar
            self.seek_slider.set(new_time)
            self.seek_audio(new_time)

    def forward_audio(self):
        """Sesi 10 saniye ileri sar."""
        if self.audio_path and pygame.mixer.music.get_busy():
            new_time = min(self.duration, self.seek_slider.get() + 10)  # 10 saniye ileri sar
            self.seek_slider.set(new_time)
            self.seek_audio(new_time)

    def add_to_favorites(self, seans):
        """Seçilen ses dosyasını favorilere ekler veya çıkarır."""
        favorites_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "favorites.json"))
        favorites = []

        # Favoriler dosyasını yükle
        if os.path.exists(favorites_file):
            with open(favorites_file, "r", encoding="utf-8") as file:
                favorites = json.load(file)

        # Favorilere ekleme veya çıkarma işlemi
        if seans["ses_dosyasi"] in favorites:
            favorites.remove(seans["ses_dosyasi"])
            with open(favorites_file, "w", encoding="utf-8") as file:
                json.dump(favorites, file, ensure_ascii=False, indent=4)
            messagebox.showinfo("Favoriler", f"{seans['ses_dosyasi']} favorilerden çıkarıldı!")
        else:
            favorites.append(seans["ses_dosyasi"])
            with open(favorites_file, "w", encoding="utf-8") as file:
                json.dump(favorites, file, ensure_ascii=False, indent=4)
            messagebox.showinfo("Favoriler", f"{seans['ses_dosyasi']} favorilere eklendi!")
