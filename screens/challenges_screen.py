import customtkinter as ctk
from screens.base_screen import BaseScreen

class ChallengesScreen(BaseScreen):
    def __init__(self, master, go_back, bölüm):
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
            fg_color="#212121",
            hover_color="#312e33"
        )
        back_btn.place(x=10, y=10)

        # Meydan okumalar için bir çerçeve
        challenges_frame = ctk.CTkFrame(
            self,
            fg_color=self.cget("fg_color"),
            corner_radius=20
        )
        challenges_frame.place(relx=0.5, rely=0.2, anchor="n")  # Çerçeveyi ortala

        # Meydan okumaları listele
        for i, seans in enumerate(bölüm["seanslar"]):
            row = i // 2
            col = i % 2
            challenge_btn = ctk.CTkButton(
                challenges_frame,
                text=seans["isim"],
                command=lambda s=seans: self.master.show_meditation(s),  # Meditasyon ekranını aç
                width=200,
                height=50,
                font=("Times New Roman", 12, "bold"),
            )
            challenge_btn.grid(row=row, column=col, padx=10, pady=10)