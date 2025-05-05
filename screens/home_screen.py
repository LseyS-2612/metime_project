import customtkinter as ctk
import json
import random
from utils.data_manager import load_meditation_data, update_streak
from PIL import Image, ImageTk, ImageDraw
import os
import datetime

class HomeScreen(ctk.CTkFrame):
    def __init__(self, master, go_meditation, go_settings):
        super().__init__(master)

        self.go_meditation = go_meditation

        # Menü çerçevesi
        menu_frame = ctk.CTkFrame(self, height=60, fg_color="#343434")
        menu_frame.pack(side="top", fill="x")

        # Günün saatine göre selamlama mesajı
        self.greeting_label = ctk.CTkLabel(
            menu_frame,
            text=self.get_greeting_message(),
            font=("Times New Roman", 24, "bold"),  # Daha büyük ve italik bir yazı tipi
            text_color="#FFFFFF"  # Beyaz renk
        )
        self.greeting_label.place(x=15, y=15)  # Sol üst köşeye yerleştir

        # Streak bilgisi (ikon olarak)
        streak = load_meditation_data().get("streak", 0)
        streak_icon = ctk.CTkLabel(
            menu_frame,
            text=f"🔥 {streak}",
            font=("Arial", 14, "bold"),  # Daha küçük ve ikon stili
            text_color="#FFFFFF"
        )
        streak_icon.place(x=500, y=15)  # Ayarlar ikonunun soluna yerleştir

        # Ayarlar butonu
        settings_btn = ctk.CTkButton(
            menu_frame,
            text="⚙️",  # İkon olarak gösterilecek
            width=40,
            height=40,
            command=go_settings,
            fg_color="#212121",  # Arka planı şeffaf yap
            hover_color="#312e33"  # Üzerine gelindiğinde renk değişimi
        )
        settings_btn.place(x=550, y=10)  # Sağ üst köşeye yerleştir

        # Butonlar için bir çerçeve
        button_frame = ctk.CTkFrame(self)
        button_frame.place(relx=0.5, rely=0.15, anchor="n")  # Menü çerçevesi için daha aşağıya taşındı

        # Buton isimleri ve işlevleri
        buttons = [
            ("Günlük Meditasyon", lambda: print("Günlük Meditasyon")),
            ("İndirilenler", lambda: print("İndirilenler")),
            ("Zamanlayıcı", self.show_timer_screen),
            ("Uyku", lambda: print("Uyku")),
            ("Meydan Okuma", lambda: print("Meydan Okuma")),
            ("Acil Durum", lambda: print("Acil Durum")),
            ("Favoriler", lambda: print("Favoriler")),
            ("Kurslar", self.show_course_categories)
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
                height=50
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

    def update_quote(self):
        """Sözleri ve arka planı rastgele seç ve etiketi güncelle."""
        if self.quotes and self.background_images:
            # Rastgele bir söz ve arka plan resmi seç
            random_quote = random.choice(self.quotes)
            random_image_path = random.choice(self.background_images)

            # Resmi yükle ve boyutlandır
            image = Image.open(random_image_path).resize((500, 150))  # Çerçeve boyutuna göre yeniden boyutlandır

            # Köşeleri yuvarlak hale getirmek için maske oluştur
            mask = Image.new("L", image.size, 0)
            draw = ImageDraw.Draw(mask)
            corner_radius = 30  # Yuvarlaklık derecesi
            draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius=corner_radius, fill=255)

            # Maskeyi uygula
            image = image.convert("RGBA")
            rounded_image = Image.new("RGBA", image.size)
            rounded_image.paste(image, (0, 0), mask)

            # Siyah yarı saydam katman ekle (karartma efekti)
            overlay = Image.new("RGBA", rounded_image.size, (0, 0, 0, 100))  # Siyah yarı saydam katman
            rounded_overlay = Image.new("RGBA", overlay.size)
            rounded_overlay.paste(overlay, (0, 0), mask)  # Maskeyi karartma efektine uygula

            # Karartma efektini resme uygula
            rounded_image = Image.alpha_composite(rounded_image, rounded_overlay)

            # Resmi tkinter uyumlu hale getir
            self.background_image = ImageTk.PhotoImage(rounded_image)

            # Arka plan resmini çerçeveye uygula
            self.quote_label.configure(image=self.background_image, text="")  # Resmi göster

            # Alıntıyı metin olarak ekle
            self.quote_label.configure(
                text=f'"{random_quote["quote"]}"\n\n- {random_quote["author"]}',
                font=("Times New Roman", 20, "bold"),
                compound="center"  # Resim ve metni birleştir
            )
        # 10 saniye sonra tekrar güncelle
        self.after(100000, self.update_quote)

    def show_course_categories(self):
        """'Kurslar' butonuna tıklandığında bölümleri 2x10 düzeninde gösterir."""
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
                    height=50
                )
                category_btn.grid(row=row, column=col, padx=10, pady=10)

        except FileNotFoundError:
            print("courses.json dosyası bulunamadı!")

    def show_sessions(self, bölüm):
        """Seçilen bölümdeki seansları 2x10 düzeninde gösterir."""
        # Önce mevcut içerikleri temizle
        for widget in self.winfo_children():
            widget.destroy()

        # Geri dönüş butonu (sol üst köşede ikon olarak)
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",  # Geri dönüş ikonu
            width=40,
            height=40,
            command=self.show_course_categories,  # Kurs kategorilerine dönmek için
            fg_color="#212121",  # Arka plan rengi
            hover_color="#312e33"  # Üzerine gelindiğinde renk değişimi
        )
        back_btn.place(x=10, y=10)  # Sol üst köşeye yerleştir

        # Seanslar için bir çerçeve
        sessions_frame = ctk.CTkFrame(self)
        sessions_frame.place(relx=0.5, rely=0.2, anchor="n")  # Çerçeveyi ortala

        # 2x10 düzeni
        for i, seans in enumerate(bölüm["seanslar"]):
            row = i // 2
            col = i % 2
            session_btn = ctk.CTkButton(
                sessions_frame,
                text=f"{seans['isim']} ({seans['süre']} dk)",
                command=lambda s=seans: self.start_meditation(s["süre"]),
                width=200,
                height=50
            )
            session_btn.grid(row=row, column=col, padx=10, pady=10)

    def load_home_screen(self):
        """Ana ekrana dönmek için."""
        self.master.show_home()

    def start_meditation(self, süre):
        """Meditasyonu başlatır."""
        print(f"{süre} dakikalık meditasyon başlıyor!")
        self.go_meditation(süre)

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
        start_btn = ctk.CTkButton(
            self,
            text="Başlat",
            command=lambda: self.start_timer(time_entry.get()),
            width=100,
            height=40,
            fg_color="#4CAF50",  # Yeşil renk
            hover_color="#45A049"
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
        self.pause_btn = ctk.CTkButton(
            self,
            text="Duraklat",
            width=100,
            height=40,
            command=self.toggle_pause,
            fg_color="#FFA500",  # Turuncu renk
            hover_color="#FF8C00"
        )
        self.pause_btn.place(relx=0.5, rely=0.6, anchor="center")

        # Geri sayımı başlat
        self.remaining_seconds = minutes * 60
        self.update_countdown()

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
