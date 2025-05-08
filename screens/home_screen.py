import customtkinter as ctk
import json
import random
from utils.data_manager import load_meditation_data, update_streak, load_settings , load_audio_files,start_daily_meditation
from PIL import Image, ImageTk, ImageDraw, ImageOps, ImageEnhance
import os
import datetime
from screens.profile_screen import ProfileScreen
from screens.settings_screen import SettingsScreen
import pygame


class HomeScreen(ctk.CTkFrame):
    def __init__(self, master, go_meditation, go_settings, go_profile):
        super().__init__(master)

        self.go_meditation = go_meditation
        self.go_settings = go_settings
        self.go_profile = go_profile

        # Menü çerçevesi
        menu_frame = ctk.CTkFrame(self, height=60, fg_color="#343434")
        menu_frame.pack(side="top", fill="x")

        # # Günün saatine göre selamlama mesajı
        # self.greeting_label = ctk.CTkLabel(
        #     menu_frame,
        #     text=self.get_greeting_message(),
        #     font=("Times New Roman", 20, "bold"),  # Daha büyük ve italik bir yazı tipi
        #     text_color="#FFFFFF"  # Beyaz renk
        # )
        # self.greeting_label.place(relx=15, rely=15)  # Sol üst köşeye yerleştir

        self.application_name_label = ctk.CTkLabel(
            menu_frame,
            text="MeTime",
            font=("Verdana", 28, "bold"),  # Daha büyük ve italik bir yazı tipi
            text_color="#FFFFFF"  # Beyaz renk
        )
        self.application_name_label.place(relx=0.5, rely=0.5, anchor="center")  # Ortalanmış şekilde yerleştir

        # Streak bilgisi (ikon olarak)
        streak = load_meditation_data().get("streak", 0)
        streak_icon = ctk.CTkLabel(
            menu_frame,
            text=f"🔥 {streak}",
            font=("Arial", 14, "bold"),  # Daha küçük ve ikon stili
            text_color="#FFFFFF"
        )
        streak_icon.place(x=460, y=18)  # Ayarlar ikonunun soluna yerleştir

        # Profil butonu
        profile_btn = ctk.CTkButton(
            menu_frame,
            text="👤",  # Profil ikonu
            width=40,
            height=40,
            command=self.go_profile,  # Profil ekranını çağır
            fg_color="#212121",
            hover_color="#312e33"
        )
        profile_btn.place(x=500, y=10)  # Streak ile ayarlar arasında yerleştirildi

        # Ayarlar butonu
        settings_btn = ctk.CTkButton(
            menu_frame,
            text="⚙️",  # İkon olarak gösterilecek
            width=40,
            height=40,
            command=lambda: self.master.show_settings(),  # Ayarlar ekranını çağır
            fg_color="#212121",  # Arka planı şeffaf yap
            hover_color="#312e33"  # Üzerine gelindiğinde renk değişimi
        )
        settings_btn.place(x=550, y=10)  # Sağ üst köşeye yerleştir

        # Butonlar için bir çerçeve
        button_frame = ctk.CTkFrame(self)
        button_frame.place(relx=0.5, rely=0.15, anchor="n")  # Menü çerçevesi için daha aşağıya taşındı

        # Buton isimleri ve işlevleri
        buttons = [
            ("Günlük Meditasyon",self.start_daily_meditation),
            ("İndirilenler", lambda: print("İndirilenler")),
            ("Zamanlayıcı", self.show_timer_screen),
            ("Uyku", lambda: self.show_sleep_sessions()),
            ("Meydan Okuma", lambda: print("Meydan Okuma")),
            ("Acil Durum", lambda: print("Acil Durum")),
            ("Favoriler", lambda: print("Favoriler")),
            ("Kurslar", self.show_course_categories),
        ]

        # 3 satır ve 2 sütun düzeni
        for i, (text, command) in enumerate(buttons):
            row = i // 2
            col = i % 2
            btn = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                width=200,
                height=50,
                font=("Times New Roman", 16, "bold"),
                corner_radius=20,  # Köşeleri yuvarlat
            )
            btn.grid(row=row, column=col, padx=10, pady=10)

        # Tıklanabilir büyük alan (daha yukarıda, köşeleri yuvarlatılmış)
        self.quote_frame = ctk.CTkFrame(
            self,
            width=500,
            height=150,
            fg_color=self.cget("fg_color"),  # Temadaki genel arka plan rengini kullan
            corner_radius=50  # Köşeleri yuvarlat
        )
        self.quote_frame.place(relx=0.5, rely=0.75, anchor="center")  # Daha yukarı taşımak için rely değerini azalttık

        self.quote_label = ctk.CTkLabel(
            self.quote_frame,
            text="",
            font=("Times New Roman", 20, "bold"),
            wraplength=480,
            justify="center",
            anchor="center"
        )
        self.quote_label.place(relx=0.5, rely=0.5, anchor="center")  # Ortaya yerleştir

        # Resimleri ve sözleri yükle
        self.quotes = self.load_quotes()
        self.background_images = self.load_background_images()

        # Sözleri ve arka planı güncelle
        self.update_quote()

    def get_greeting_message(self):
        """Günün saatine göre selamlama mesajı döndürür."""
        current_hour = datetime.datetime.now().hour
        if 5 <= current_hour < 12:
            return "Günaydın!"
        elif 12 <= current_hour < 18:
            return "İyi Günler!"
        elif 18 <= current_hour < 22:
            return "İyi Akşamlar!"
        else:
            return "İyi Geceler!"

    def load_quotes(self):
        """JSON dosyasından sözleri yükler."""
        try:
            base_dir = os.path.dirname(__file__)
            file_path = os.path.abspath(os.path.join(base_dir, "..", "quotes.json"))

            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print("quotes.json dosyası bulunamadı!")
            return []

    def load_background_images(self):
        """Arka plan resimlerini yükler."""
        base_dir = os.path.dirname(__file__)
        backgrounds_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "backgrounds"))

        try:
            return [
                os.path.join(backgrounds_path, file)
                for file in os.listdir(backgrounds_path)
                if file.lower().endswith((".png", ".jpg", ".jpeg"))
            ]
        except FileNotFoundError:
            print("Arka plan klasörü bulunamadı!")
            return []


    def start_daily_meditation(self):
        """Günlük meditasyon için rastgele bir ses dosyasını çalar ve meditasyon ekranını açar."""
        start_daily_meditation(load_audio_files, self.master.show_screen, self.master.show_home)

    def show_sleep_sessions(self):
        """'Uyku' butonuna tıklandığında 'Uyku İçin Meditasyon' bölümündeki seansları gösterir."""
        # Önce mevcut içerikleri temizle
        for widget in self.winfo_children():
            widget.destroy()

        # Geri dönüş butonu
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",
            width=40,
            height=40,
            command=self.load_home_screen,  # Ana ekrana dönmek için
            fg_color="#212121",
            hover_color="#312e33"
        )
        back_btn.place(x=10, y=10)

        # Seanslar için bir çerçeve
        sessions_frame = ctk.CTkFrame(self)
        sessions_frame.place(relx=0.5, rely=0.2, anchor="n")

        # "Uyku İçin Meditasyon" bölümünü yükle
        try:
            base_dir = os.path.dirname(__file__)
            file_path = os.path.abspath(os.path.join(base_dir, "..", "courses.json"))

            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # "Uyku İçin Meditasyon" bölümünü bul
            sleep_section = next((bölüm for bölüm in data["Bölümler"] if bölüm["isim"] == "Uyku İçin Meditasyon"), None)

            if sleep_section:
                # 2x10 düzeni
                for i, seans in enumerate(sleep_section["seanslar"]):
                    row = i // 2
                    col = i % 2
                    session_btn = ctk.CTkButton(
                        sessions_frame,
                        text=f"{seans['isim']}",
                        command=lambda s=seans: self.start_meditation(s),
                        width=200,
                        height=50,
                        font=("Times New Roman", 12, "bold"),
                    )
                    session_btn.grid(row=row, column=col, padx=10, pady=10)
            else:
                print("'Uyku İçin Meditasyon' bölümü bulunamadı!")

        except FileNotFoundError:
            print("courses.json dosyası bulunamadı!")



    def update_quote(self):
        """Sözleri ve arka planı rastgele seç ve etiketi güncelle."""
        if self.quotes and self.background_images:
            # Rastgele bir söz ve arka plan resmi seç
            random_quote = random.choice(self.quotes)
            random_image_path = random.choice(self.background_images)

            # Resmi yükle ve karartma işlemi uygula
            image = Image.open(random_image_path).resize((500, 150), Image.Resampling.LANCZOS)
            enhancer = ImageEnhance.Brightness(image)
            darkened_image = enhancer.enhance(0.5)  # Parlaklığı %50 azalt

            # Yuvarlak köşeli hale getir
            rounded_image = self.make_rounded_image(darkened_image, (500, 150))
            ctk_image = ctk.CTkImage(rounded_image, size=(500, 150))  # CTkImage kullanımı

            # Arka plan resmini çerçeveye uygula
            self.quote_label.configure(image=ctk_image, text="")  # Resmi göster
            self.quote_label.image = ctk_image  # Referansı sakla

            # Alıntıyı metin olarak ekle
            self.quote_label.configure(
                text=f'"{random_quote["quote"]}"\n\n- {random_quote["author"]}',
                font=("Verdana", 16, "bold"),
                compound="center"  # Resim ve metni birleştir
            )
        # 10 saniye sonra tekrar güncelle
        self.after(100000, self.update_quote)

    def make_rounded_image(self, image, size):
        """Bir görüntüyü yuvarlak köşeli hale getirir."""
        image = image.resize(size, Image.Resampling.LANCZOS)  # LANCZOS kullanımı
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, size[0], size[1]), radius=30, fill=255)  # Köşe yuvarlatma
        rounded_image = ImageOps.fit(image, size, centering=(0.5, 0.5))
        rounded_image.putalpha(mask)
        return rounded_image

    def show_course_categories(self):
        """'Kurslar' butonuna tıklandığında bölümleri 2x10 düzeninde gösterir."""
        # Önce mevcut içerikleri temizle
        menu_frame = ctk.CTkFrame(self, height=60, fg_color="#343434")
        menu_frame.pack(side="top", fill="x")
        


        for widget in self.winfo_children():
            widget.destroy()

        # Geri dönüş butonu (sol üst köşede ikon olarak)
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",  # Geri dönüş ikonu
            width=40,
            height=40,
            command=self.load_home_screen,  # Ana ekrana dönmek için
            fg_color="#212121",  # Arka plan rengi
            hover_color="#312e33"  # Üzerine gelindiğinde renk değişimi
        )
        back_btn.place(x=10, y=10)  # Sol üst köşeye yerleştir

        # Kurslar için bir çerçeve
        courses_frame = ctk.CTkFrame(self)
        courses_frame.place(relx=0.5, rely=0.2, anchor="n")  # Çerçeveyi ortala

        # Bölümleri yükle
        try:
            base_dir = os.path.dirname(__file__)
            file_path = os.path.abspath(os.path.join(base_dir, "..", "courses.json"))

            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # 2x10 düzeni
            for i, bölüm in enumerate(data["Bölümler"]):
                row = i // 2
                col = i % 2
                category_btn = ctk.CTkButton(
                    courses_frame,
                    text=bölüm["isim"],
                    command=lambda b=bölüm: self.show_sessions(b),
                    width=200,
                    height=50,
                    font=("Times New Roman", 12, "bold"),

                )
                category_btn.grid(row=row, column=col, padx=10, pady=10)

        except FileNotFoundError:
            print("courses.json dosyası bulunamadı!")

    def show_sessions(self, bölüm):
        """Seçilen bölümdeki seansları 2x10 düzeninde gösterir."""
        # Önce mevcut içerikleri temizle
        for widget in self.winfo_children():
            widget.destroy()

        # Geri dönüş butonu
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",
            width=40,
            height=40,
            command=self.show_course_categories,
            fg_color="#212121",
            hover_color="#312e33"
        )
        back_btn.place(x=10, y=10)
        # Seanslar için bir çerçeve
        sessions_frame = ctk.CTkFrame(self)
        sessions_frame.place(relx=0.5, rely=0.5, anchor="center")  # Çerçeveyi ortala

        # 2x10 düzeni
        for i, seans in enumerate(bölüm["seanslar"]):
            row = i // 2
            col = i % 2
            session_btn = ctk.CTkButton(
            sessions_frame,
            text=f"{seans['isim']}",
            command=lambda s=seans: self.start_meditation(s),
            width=200,
            height=50,
            font=("Times New Roman", 12, "bold"),
            )
            session_btn.grid(row=row, column=col, padx=10, pady=10)

    def play_audio(self, seans):
        audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio"))
        audio_path = os.path.join(audio_dir, seans["ses_dosyasi"])

        if os.path.exists(audio_path):
            duration = self.get_audio_duration(audio_path)
            print(f"Ses dosyasının süresi: {duration} saniye")
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
        else:
            print(f"Ses dosyası bulunamadı: {audio_path}")

    def get_audio_duration(self,audio_path):
        pygame.mixer.init()
        sound = pygame.mixer.Sound(audio_path)
        duration = sound.get_length()  # Süreyi saniye cinsinden alır
        return duration

    def load_home_screen(self):
        """Ana ekrana dönmek için."""
        self.master.show_home()

    def start_meditation(self, seans):
        """Meditasyonu başlatır."""
        print(f"{seans['isim']} meditasyonu başlıyor!")
        self.go_meditation(seans)

    def show_timer_screen(self):
        """Zamanlayıcı ekranını gösterir."""
        # Önce mevcut içerikleri temizle
        for widget in self.winfo_children():
            widget.destroy()

        # Geri dönüş butonu (sol üst köşede ikon olarak)
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",  # Geri dönüş ikonu
            width=40,
            height=40,
            command=self.load_home_screen,  # Ana ekrana dönmek için
            fg_color="#212121",  # Arka plan rengi
            hover_color="#312e33"  # Üzerine gelindiğinde renk değişimi
        )
        back_btn.place(x=10, y=10)  # Sol üst köşeye yerleştir

        # Zamanlayıcı başlığı
        timer_label = ctk.CTkLabel(
            self,
            text="Zamanlayıcı Kur",
            font=("Helvetica", 20, "bold"),
            text_color="#FFFFFF"
        )
        timer_label.place(relx=0.5, rely=0.2, anchor="center")

        # Süre seçimi için giriş alanı
        time_entry = ctk.CTkEntry(
            self,
            placeholder_text="Süreyi dakika olarak girin",
            width=200,
            height=40
        )
        time_entry.place(relx=0.5, rely=0.4, anchor="center")

        # Zamanlayıcıyı başlatma butonu
        button_colors = self.get_timer_button_color()  # Temaya uygun renkler al
        start_btn = ctk.CTkButton(
            self,
            text="Başlat",
            command=lambda: self.start_timer(time_entry.get()),
            width=100,
            height=40,
            fg_color=button_colors["fg_color"],  # Temaya uygun renk
            hover_color=button_colors["hover_color"],
            corner_radius=20  
        )
        start_btn.place(relx=0.5, rely=0.5, anchor="center")

    def start_timer(self, minutes):
        """Zamanlayıcıyı başlatır."""
        try:
            minutes = int(minutes)
            if minutes <= 0:
                raise ValueError("Süre pozitif bir sayı olmalıdır.")
        except ValueError:
            error_label = ctk.CTkLabel(
                self,
                text="Lütfen geçerli bir süre girin!",
                font=("Helvetica", 14, "bold"),
                text_color="#FF0000"  # Kırmızı renk
            )
            error_label.place(relx=0.5, rely=0.6, anchor="center")
            self.after(3000, error_label.destroy)  # 3 saniye sonra hata mesajını kaldır
            return

        # Geri sayım ekranını göster
        self.show_countdown(minutes)

    def show_countdown(self, minutes):
        """Geri sayım ekranını gösterir."""
        # Önce mevcut içerikleri temizle
        for widget in self.winfo_children():
            widget.destroy()

        # Geri dönüş butonu
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",
            width=40,
            height=40,
            command=self.load_home_screen,
            fg_color="#212121",
            hover_color="#312e33"
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
        button_colors = self.get_timer_button_color()  # Temaya uygun renkler al
        self.pause_btn = ctk.CTkButton(
            self,
            text="Duraklat",
            width=100,
            height=40,
            command=self.toggle_pause,
            fg_color=button_colors["fg_color"],  # Temaya uygun renk
            hover_color=button_colors["hover_color"]  # Temaya uygun hover rengi
        )
        self.pause_btn.place(relx=0.5, rely=0.6, anchor="center")

        # Geri sayımı başlat
        self.remaining_seconds = minutes * 60
        self.update_countdown()

    def get_timer_button_color(self):
        """Temaya uygun başlat/duraklat butonu renklerini döndürür."""
        theme = self.get_theme()
        if theme == "Purple & Gray":
            return {"fg_color": "#6A0DAD", "hover_color": "#7B1FA2"}  # Mor tonları
        elif theme == "Orange & Gray":
            return {"fg_color": "#FF5722", "hover_color": "#FF7043"}  # Turuncu tonları
        return {"fg_color": "#4CAF50", "hover_color": "#45A049"}  # Varsayılan yeşil

    def get_theme(self):
        """Temayı ayarlardan alır."""
        settings = load_settings()
        return settings.get("theme", "Purple & Gray")

    def toggle_pause(self):
        """Duraklatma ve devam etme işlemini kontrol eder."""
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.configure(text="Başlat")  # Buton metnini "Başlat" olarak değiştir
        else:
            self.pause_btn.configure(text="Duraklat")  # Buton metnini "Duraklat" olarak değiştir
            self.update_countdown()  # Geri sayımı devam ettir

    def update_countdown(self):
        """Geri sayımı günceller."""
        if self.paused:
            return  # Duraklatılmışsa hiçbir şey yapma

        if self.remaining_seconds > 0:
            minutes = self.remaining_seconds // 60
            seconds = self.remaining_seconds % 60
            self.countdown_label.configure(text=f"{minutes:02}:{seconds:02}")
            self.remaining_seconds -= 1
            self.after(1000, self.update_countdown)
        else:
            self.countdown_label.configure(text="Süre Doldu!")

    def show_profile_screen(self):
        """Profil ekranını gösterir."""
        self.master.clear_frame()
        self.master.current_frame = ProfileScreen(self.master, self.master.show_home)
        self.master.current_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
