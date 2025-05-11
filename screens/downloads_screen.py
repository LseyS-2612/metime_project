import customtkinter as ctk
import os
import shutil
import json
from screens.base_screen import BaseScreen
from tkinter import filedialog, messagebox

class DownloadsScreen(BaseScreen):
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
            width=30,
            height=30,
            command=go_back,  # Ana ekrana geri dönmek için
            fg_color=self.master.theme_colors["fg_color"],  # Temaya uygun renk
            hover_color=self.master.theme_colors["hover_color"]  # Temaya uygun hover rengi
        )
        back_btn.place(x=10, y=10)

        # Kaydırılabilir çerçeve
        scrollable_frame = ctk.CTkScrollableFrame(
            self,
            width=550,
            height=700,
            fg_color=self.cget("fg_color"),
            corner_radius=10
        )
        scrollable_frame.place(relx=0.5, rely=0.05, anchor="n")  # Daha yukarıya taşındı

        # courses.json dosyasından MP3 dosyalarını listele
        courses_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "courses.json"))
        if os.path.exists(courses_path):
            with open(courses_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            seanslar = []
            for bölüm in data.get("Bölümler", []):
                seanslar.extend(bölüm.get("seanslar", []))

            if seanslar:
                for i, seans in enumerate(seanslar):
                    file_name = seans.get("isim", "Bilinmeyen")
                    file_path = seans.get("ses_dosyasi", "")

                    row = i // 2
                    col = i % 2

                    # Seans adı
                    file_label = ctk.CTkLabel(
                        scrollable_frame,
                        text=file_name,
                        font=("Times New Roman", 10, "bold"),
                        text_color="#FFFFFF"
                    )
                    file_label.grid(row=row, column=col * 2, padx=5, pady=5)

                    # İndirme butonu
                    download_btn = ctk.CTkButton(
                        scrollable_frame,
                        text="İndir",
                        command=lambda f=file_path: self.download_file(f),
                        width=80,
                        height=30,
                        fg_color=self.master.theme_colors["fg_color"],  # Temaya uygun renk
                        hover_color=self.master.theme_colors["hover_color"],  # Temaya uygun hover rengi
                        corner_radius=10
                    )
                    download_btn.grid(row=row, column=col * 2 + 1, padx=5, pady=5)
            else:
                error_label = ctk.CTkLabel(
                    self,
                    text="MP3 dosyası bulunamadı!",
                    font=("Helvetica", 12, "bold"),
                    text_color="#FF0000"
                )
                error_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            error_label = ctk.CTkLabel(
                self,
                text="courses.json dosyası bulunamadı!",
                font=("Helvetica", 12, "bold"),
                text_color="#FF0000"
            )
            error_label.place(relx=0.5, rely=0.5, anchor="center")

    def download_file(self, file_path):
        """Belirtilen dosyayı kullanıcı tarafından seçilen bir konuma indirir."""
        if not file_path:
            messagebox.showerror("Hata", "Dosya yolu bulunamadı!")
            return

        audio_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", file_path))
        if not os.path.exists(audio_path):
            messagebox.showerror("Hata", "Dosya bulunamadı!")
            return

        save_path = filedialog.asksaveasfilename(
            initialfile=os.path.basename(file_path),
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        if save_path:
            try:
                shutil.copy(audio_path, save_path)
                messagebox.showinfo("Başarılı", f"Dosya başarıyla indirildi: {save_path}")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya indirilemedi: {str(e)}")