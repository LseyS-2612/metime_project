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
from utils.data_manager import load_settings, save_settings, load_meditation_data, update_streak


class MeditationScreen(BaseScreen):
    def __init__(self, master, go_home, seans):
        super().__init__(master)
        self.master = master
        self.go_home = go_home
        self.running = False
        self.paused = False
        self.audio_path = None
        self.start_time =0
        self.pause_time=0
        self.elapsed_time =0
        self.selected_audio_path = None  # Seçilen ses dosyasının yolu
        self.audio_playing = False  # Ses oynatma durumu (Başlangıçta False)
        self.current_position = 0  # Çalma konumunu takip eder
        self.hide_slider_job = None

        # Zaman alan işlemleri ayrı bir iş parçacığında çalıştır
        threading.Thread(target=self.setup_meditation_screen, args=(seans,), daemon=True).start()

    def setup_meditation_screen(self, seans):
        """Meditasyon ekranını hazırlar."""
        threading.Thread(target=self.load_resources, args=(seans,), daemon=True).start()

    def load_resources(self, seans):
        """Zaman alan işlemleri yükler."""
        # Ses dosyasını al ve süresini belirle
        self.audio_path = self.get_audio_path(seans)
        if self.audio_path:
            self.remaining = self.duration  # Süreyi geri sayım için ayarla

        # Favoriler dosyasını kontrol et
        favorites_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "favorites.json"))
        is_favorite = False
        if os.path.exists(favorites_file):
            with open(favorites_file, "r", encoding="utf-8") as file:
                favorites = json.load(file)
                is_favorite = seans in favorites["seanslar"]

        # Kullanıcı arayüzünü güncelle
        self.master.after(0, self.update_ui, is_favorite, seans)

    def update_ui(self, is_favorite, seans):
        """Kullanıcı arayüzünü günceller."""
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
            text="⭐ Favorilerden Çıkar" if is_favorite else "⭐ Favorilere Ekle",
            command=lambda: self.add_to_favorites(seans),
            width=200,
            height=40
        )
        self.add_to_favorites_btn.pack(pady=10)  # Başlat butonunun altına ekleniyor

        # Ses kontrol paneli
        self.audio_control_panel = ctk.CTkFrame(self, fg_color="#2E2E2E", corner_radius=10, height=30)
        self.audio_control_panel.pack(pady=20, fill="x", padx=40)  # Paneli biraz daha alta al

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
        if self.audio_path:
            # Çalma konumunu güncelle
            self.current_position = float(value)
            self.elapsed_time = self.current_position  # Geçen süreyi de güncelle
            self.start_time = time.time() - self.elapsed_time  # Başlangıç zamanını güncelle

            # Eğer ses çalıyorsa, yeni konumdan başlat
            if self.running and not self.paused:
                pygame.mixer.music.stop()
                pygame.mixer.music.play(start=self.current_position)

            # Timer'ı güncelle
            self.remaining = self.duration - int(value)
            self.timer_label.configure(text=self.format_time(self.remaining))

    def start_or_pause_meditation(self):
        """Meditasyonu ve arka plan sesini başlat veya duraklat."""
        if not self.running:
            # Eğer meditasyon sıfırlanmışsa (bittiği için)
            if self.remaining == 0:
                self.remaining = self.duration  # Süreyi baştan başlat
                self.seek_slider.set(0)  # Slider'ı başa al
                self.current_position = 0  # Pozisyonu sıfırla
                self.elapsed_time = 0  # Geçen süreyi sıfırla
                self.timer_label.configure(text=self.format_time(self.remaining))  # Timer'ı güncelle

            # Meditasyonu başlat
            self.running = True
            self.paused = False
            self.start_pause_btn.configure(text="⏸️ Duraklat")
            
            # Başlangıç zamanını güncelle
            self.start_time = time.time() - self.elapsed_time
            
            # Eğer meditasyon sesi çalmıyorsa başlat
            if not pygame.mixer.music.get_busy():
                if self.audio_path:
                    pygame.mixer.music.load(self.audio_path)
                    pygame.mixer.music.play(start=self.current_position)  # Kaldığı yerden başlat
                    print(f"Ses dosyası {self.current_position} saniyeden başlatıldı")  # Debug için
                else:
                    ctk.CTkLabel(self, text="⚠️ Ses dosyası bulunamadı!", font=("Arial", 14, "bold"), fg_color="red").pack(pady=10)
                    return
            else:
                pygame.mixer.music.unpause()  # Eğer duraklatılmışsa devam ettir
                print("Ses dosyası devam ettiriliyor")  # Debug için

            # Timer thread'i başlat
            threading.Thread(target=self.run_timer, daemon=True).start()
        elif self.paused:
            # Duraklatıldıysa devam et
            self.paused = False
            self.running = True
            self.start_pause_btn.configure(text="⏸️ Duraklat")
            # Başlangıç zamanını güncelle
            self.start_time = time.time() - self.elapsed_time
            
            pygame.mixer.music.unpause()  # Meditasyon sesini devam ettir
            print("Ses dosyası devam ettiriliyor")  # Debug için
        else:
            # Devam ediyorsa duraklat
            self.paused = True
            self.running = False
            self.start_pause_btn.configure(text="▶️ Devam Et")
            
            # Geçen süreyi hesapla
            self.elapsed_time = time.time() - self.start_time
            self.current_position = self.elapsed_time  # Geçen süreyi pozisyon olarak kullan
            
            pygame.mixer.music.pause()  # Meditasyon sesini duraklat
            print(f"Duraklatıldı, konum: {self.current_position:.3f} saniye")  # Debug için


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
        """Timer'ı çalıştır ve ses dosyasının ilerlemesini takip et."""
        while self.running:
            if not self.paused:
                # Geçen süreyi güncelle
                current_time = time.time()
                self.elapsed_time = current_time - self.start_time
                
                # Ses dosyasının konumunu get_pos() ile al (milisaniye cinsinden)
                music_pos = pygame.mixer.music.get_pos()
                
                # Eğer ses çalıyorsa ve konum 0'dan büyükse, current_position'ı güncelle
                if pygame.mixer.music.get_busy() and music_pos > 0:
                    self.current_position = self.elapsed_time
            
                # Slider'ı güncelle
                if self.elapsed_time <= self.duration:
                    self.master.after(0, lambda: self.seek_slider.set(self.current_position))
                
                # Timer'ı güncelle
                self.remaining = max(0, self.duration - int(self.current_position))
                self.master.after(0, lambda r=self.remaining: self.timer_label.configure(text=self.format_time(r)))
                
                if self.elapsed_time >= self.duration:
                    self.master.after(0, self.end_session)
                    break
            
            time.sleep(0.1)  # CPU kullanımını azaltmak için küçük bir gecikme

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
        pygame.mixer.Channel(2).stop()  # Arka plan sesini durdur
        self.go_home()  # Ana ekrana dön

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
        """Seçilen seansı favorilere ekler veya çıkarır ve butonun metnini günceller."""
        favorites_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "favorites.json"))
        favorites = {"seanslar": []}

        # Favoriler dosyasını yükle
        if os.path.exists(favorites_file):
            with open(favorites_file, "r", encoding="utf-8") as file:
                favorites = json.load(file)

        # Favorilere ekleme veya çıkarma işlemi
        if seans in favorites["seanslar"]:
            favorites["seanslar"].remove(seans)
            with open(favorites_file, "w", encoding="utf-8") as file:
                json.dump(favorites, file, ensure_ascii=False, indent=4)
            messagebox.showinfo("Favoriler", f"{seans['isim']} favorilerden çıkarıldı!")
            self.add_to_favorites_btn.configure(text="⭐ Favorilere Ekle")  # Buton metnini güncelle
        else:
            favorites["seanslar"].append(seans)
            with open(favorites_file, "w", encoding="utf-8") as file:
                json.dump(favorites, file, ensure_ascii=False, indent=4)
            messagebox.showinfo("Favoriler", f"{seans['isim']} favorilere eklendi!")
            self.add_to_favorites_btn.configure(text="⭐ Favorilerden Çıkar")  # Buton metnini güncellem

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
        else:
            print("background_sounds.json dosyası bulunamadı!")

    def select_audio_file(self, selection):
        """Seçilen ses dosyasını ayarlar."""
        for sound in self.background_sounds:
            if sound["name"] == selection:
                audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "Arka Plan Sesleri"))
                self.selected_audio_path = os.path.join(audio_dir, sound["file"])
                print(f"Seçilen ses dosyası: {self.selected_audio_path}")
                break

    def toggle_audio_playback(self):
        """Seçilen ses dosyasını başlatır veya durdurur."""
        if not self.selected_audio_path or not os.path.exists(self.selected_audio_path):
            print("Ses dosyası bulunamadı!")
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
            print(f"Arkaplan sesi başlatıldı ve sürekli çalacak: {self.selected_audio_path}")

    def change_audio_volume(self, value):
        """Ses dosyasının ses seviyesini değiştirir."""
        pygame.mixer.Channel(2).set_volume(float(value))
