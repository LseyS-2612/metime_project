import customtkinter as ctk
from screens.base_screen import BaseScreen
from screens.countdown_screen import CountdownScreen  # CountdownScreen'i içe aktar

class TimerScreen(BaseScreen):
    def __init__(self, master, go_back):
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

        # Zamanlayıcı başlığı
        timer_label = ctk.CTkLabel(
            self,
            text="Zamanlayıcı Kur",
            font=("Helvetica", 20, "bold"),
            text_color="#FFFFFF"
        )
        timer_label.place(relx=0.5, rely=0.2, anchor="center")

        # Süre seçimi için giriş alanı
        self.time_entry = ctk.CTkEntry(
            self,
            placeholder_text="Süreyi dakika olarak girin",
            width=200,
            height=40
        )
        self.time_entry.place(relx=0.5, rely=0.4, anchor="center")

        # Zamanlayıcıyı başlatma butonu
        start_btn = ctk.CTkButton(
            self,
            text="Başlat",
            command=self.start_timer,
            width=100,
            height=40,
            fg_color=self.master.theme_colors["fg_color"],  # Temaya uygun renk
            hover_color=self.master.theme_colors["hover_color"],  # Temaya uygun hover rengi
            corner_radius=20
        )
        start_btn.place(relx=0.5, rely=0.5, anchor="center")

    def start_timer(self):
        """Zamanlayıcıyı başlatır."""
        try:
            minutes = int(self.time_entry.get())
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
        """Geri sayım ekranını açar."""
        self.master.show_screen(CountdownScreen, self.master.show_home, minutes)