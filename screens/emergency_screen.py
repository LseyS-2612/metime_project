import customtkinter as ctk
from screens.base_screen import BaseScreen

class EmergencyScreen(BaseScreen):
    def __init__(self, master, go_back, emergency_section):
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

        # Başlık
        title_label = ctk.CTkLabel(
            self,
            text="Acil Durum Meditasyonları",
            font=("Helvetica", 20, "bold"),
            text_color="#FFFFFF"
        )
        title_label.place(relx=0.5, rely=0.2, anchor="center")

        # Meditasyon seçenekleri için bir çerçeve
        options_frame = ctk.CTkFrame(
            self,
            fg_color=self.cget("fg_color"),
            corner_radius=20
        )
        options_frame.place(relx=0.5, rely=0.3, anchor="n")

        # Meditasyonları listele
        for i, seans in enumerate(emergency_section["seanslar"]):
            row = i // 2
            col = i % 2
            option_btn = ctk.CTkButton(
                options_frame,
                text=seans["isim"],
                command=lambda s=seans: self.master.show_meditation(s),  # Seçilen meditasyonu başlat
                width=200,
                height=50,
                font=("Times New Roman", 12, "bold"),
                corner_radius=20
            )
            option_btn.grid(row=row, column=col, padx=10, pady=10)