import customtkinter as ctk
import json
import random
from utils.data_manager import load_meditation_data, update_streak
from PIL import Image, ImageTk, ImageDraw
import os

class HomeScreen(ctk.CTkFrame):
    def __init__(self, master, go_meditation, go_settings):
        super().__init__(master)

        self.go_meditation = go_meditation

        # Başlık
        title = ctk.CTkLabel(self, text="🧘 Meditasyon Uygulaması", font=("Arial", 22, "bold"))
        title.pack(pady=20)

        # Streak bilgisi
        streak = load_meditation_data().get("streak", 0)
        streak_label = ctk.CTkLabel(self, text=f"🔥 Streak: {streak} gün", font=("Arial", 16))
        streak_label.pack(pady=10)

        # Süre seçimi
        self.selected_time = ctk.IntVar(value=5)  # varsayılan 5 dakika

        time_frame = ctk.CTkFrame(self)
        time_frame.pack(pady=20)

        for minute in [5, 10, 15]:
            rb = ctk.CTkRadioButton(time_frame, text=f"{minute} dakika", variable=self.selected_time, value=minute)
            rb.pack(side="left", padx=10)

        # Başlat butonu
        start_btn = ctk.CTkButton(self, text="🕒 Meditasyona Başla", command=self.start_meditation)
        start_btn.pack(pady=20)

        # Ayarlar butonu (sağ üst köşeye taşındı)
        settings_btn = ctk.CTkButton(
            self,
            text="⚙️",  # İkon olarak gösterilecek
            width=40,
            height=40,
            command=go_settings,
            fg_color="#212121",  # Arka planı şeffaf yap
            hover_color="#312e33"  # Üzerine gelindiğinde renk değişimi
        )
        settings_btn.place(x=550, y=10)  # Sağ üst köşeye yerleştir

        # Tıklanabilir büyük alan (daha yukarıda, köşeleri yuvarlatılmış)
        self.quote_frame = ctk.CTkFrame(
            self,
            width=500,
            height=150,
            fg_color=self.cget("fg_color"),  # Temadaki genel arka plan rengini kullan
            corner_radius=50  # Köşeleri yuvarlat
        )
        self.quote_frame.place(relx=0.5, rely=0.6, anchor="center")  # Daha yukarı taşımak için rely değerini azalt

        self.quote_label = ctk.CTkLabel(
            self.quote_frame,
            text="",
            font=("Times New Roman", 18, "bold"),
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

    def load_quotes(self):
        """JSON dosyasından sözleri yükler."""
        try:
            with open("C:/Users/klcan/metime_project/quotes.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print("quotes.json dosyası bulunamadı!")
            return []

    def load_background_images(self):
        """Arka plan resimlerini yükler."""
        backgrounds_path = "c:/Users/klcan/metime_project/assets/backgrounds/"
        try:
            return [
                os.path.join(backgrounds_path, file)
                for file in os.listdir(backgrounds_path)
                if file.endswith((".png", ".jpg", ".jpeg"))
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
                font=("Times New Roman", 18, "bold"),
                compound="center"  # Resim ve metni birleştir
            )
        # 10 saniye sonra tekrar güncelle
        self.after(100000, self.update_quote)

    def on_quote_click(self, event=None):
        """Tıklama olayında yapılacak işlem."""
        print("Alıntıya tıklandı!")

    def start_meditation(self):
        selected = self.selected_time.get()
        update_streak()  # Streak'i güncelle
        self.go_meditation(selected)
