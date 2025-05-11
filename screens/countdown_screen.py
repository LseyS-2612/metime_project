import customtkinter as ctk
from screens.base_screen import BaseScreen

class CountdownScreen(BaseScreen):
    def __init__(self, master, go_back, minutes):
        super().__init__(master)

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