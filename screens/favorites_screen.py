import customtkinter as ctk
import os
import json
from screens.base_screen import BaseScreen

class FavoritesScreen(BaseScreen):
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

        # Başlık
        title_label = ctk.CTkLabel(
            self,
            text="Favoriler",
            font=("Helvetica", 20, "bold"),
            text_color="#FFFFFF"
        )
        title_label.place(relx=0.5, rely=0.2, anchor="center")

        # Favori meditasyonlar için bir çerçeve
        favorites_frame = ctk.CTkFrame(
            self,
            fg_color=self.cget("fg_color"),
            corner_radius=20
        )
        favorites_frame.place(relx=0.5, rely=0.3, anchor="n")

        # Favori meditasyonları yükle ve listele
        favorites_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "favorites.json"))
        if os.path.exists(favorites_path):
            with open(favorites_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            for i, seans in enumerate(data["seanslar"]):
                row = i // 2
                col = i % 2
                favorite_btn = ctk.CTkButton(
                    favorites_frame,
                    text=seans["isim"],
                    command=lambda s=seans: self.master.show_meditation(s),  # Seçilen meditasyonu başlat
                    width=200,
                    height=50,
                    font=("Times New Roman", 12, "bold"),
                    corner_radius=20
                )
                favorite_btn.grid(row=row, column=col, padx=10, pady=10)
        else:
            error_label = ctk.CTkLabel(
                self,
                text="Favoriler bulunamadı!",
                font=("Helvetica", 16, "bold"),
                text_color="#FF0000"
            )
            error_label.place(relx=0.5, rely=0.5, anchor="center")