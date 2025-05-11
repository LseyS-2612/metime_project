import os
import json
import customtkinter as ctk
from screens.base_screen import BaseScreen
from screens.sessions_screen import SessionsScreen  # Gerekli import

class CoursesScreen(BaseScreen):
    def __init__(self, master, go_back):
        super().__init__(master)

        # Geri dönüş butonu
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",
            width=40,
            height=40,
            command=go_back,  # Ana ekrana dönmek için
            fg_color="#212121",
            hover_color="#312e33"
        )
        back_btn.place(x=10, y=10)

        # Kurslar için bir çerçeve
        courses_frame = ctk.CTkFrame(
            self,
            fg_color=self.cget("fg_color"),
            corner_radius=20
        )
        courses_frame.place(relx=0.5, rely=0.2, anchor="n")

        # Kursları yükle
        try:
            base_dir = os.path.dirname(__file__)
            file_path = os.path.abspath(os.path.join(base_dir, "..", "courses.json"))

            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Kursları listele
            for i, bölüm in enumerate(data["Bölümler"]):
                row = i // 2
                col = i % 2
                category_btn = ctk.CTkButton(
                    courses_frame,
                    text=bölüm["isim"],
                    command=lambda b=bölüm: self.show_sessions(b),  # Bölüm seanslarını göster
                    width=200,
                    height=50,
                    font=("Times New Roman", 12, "bold"),
                )
                category_btn.grid(row=row, column=col, padx=10, pady=10)

        except FileNotFoundError:
            print("courses.json dosyası bulunamadı!")

    def show_sessions(self, bölüm):
        """Seçilen bölümdeki seansları göstermek için SessionsScreen'i açar."""
        self.master.show_screen(SessionsScreen, self.master.show_courses, bölüm)
