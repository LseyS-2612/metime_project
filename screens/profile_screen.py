import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageDraw
from utils.data_manager import load_meditation_data, save_settings, load_settings
import os
from screens.base_screen import BaseScreen

class ProfileScreen(BaseScreen):
    def __init__(self, master, go_home):
        super().__init__(master)

        self.go_home = go_home

        # Geri dönüş butonu
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",
            width=40,
            height=40,
            command=self.go_home,
            fg_color="#212121",
            hover_color="#312e33"
        )
        back_btn.place(x=10, y=10)

        # Ayarlar butonu
        settings_btn = ctk.CTkButton(
            self,
            text="⚙️",  # Ayarlar ikonu
            width=40,
            height=40,
            command=lambda: self.master.show_settings(),
            fg_color="#212121",
            hover_color="#312e33"
        )
        settings_btn.place(x=540, y=10)  # Sağ üst köşeye yerleştirildi

        # Kullanıcı fotoğrafı
        try:
            base_dir = os.path.dirname(__file__)
            photo_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "profile_photo.png"))
            photo = self.make_rounded_image(photo_path, (150, 150))  # Fotoğraf boyutu büyütüldü
            ctk_image = ctk.CTkImage(photo, size=(150, 150))  # CTkImage kullanımı
            self.photo_label = ctk.CTkLabel(self, image=ctk_image, text="")
            self.photo_label.place(relx=0.5, rely=0.2, anchor="center")  # Fotoğraf en üste
            self.photo_label.bind("<Button-1>", self.change_profile_photo)  # Tıklama olayı ekle
        except FileNotFoundError:
            print("Profil fotoğrafı bulunamadı!")

        # Kullanıcı adı
        settings = load_settings()
        name_label = ctk.CTkLabel(
            self,
            text=f"{settings.get('username', 'John Doe')}",
            font=("Helvetica", 22),  # Yazı tipi boyutu büyütüldü
            text_color="#FFFFFF"
        )
        name_label.place(relx=0.5, rely=0.35, anchor="center")  # Fotoğrafın altına yerleştirildi

        # Streak bilgisi
        streak = load_meditation_data().get("streak", 0)
        streak_label = ctk.CTkLabel(
            self,
            text=f"Streak: 🔥 {streak}",
            font=("Helvetica", 22),  # Yazı tipi boyutu büyütüldü
            text_color="#FFFFFF"
        )
        streak_label.place(relx=0.5, rely=0.42, anchor="center")  # İsmin altına yerleştirildi

        # Kullanıcı hakkında bilgi
        about_label = ctk.CTkLabel(
            self,
            text=f"Hakkımda: {settings.get('about', 'Meditasyon yapmayı seviyorum.')}",
            font=("Helvetica", 20),  # Yazı tipi boyutu büyütüldü
            text_color="#FFFFFF",
            wraplength=450,  # Yazı genişliği artırıldı
            justify="center"
        )
        about_label.place(relx=0.5, rely=0.50, anchor="center")  # Streak'in altına yerleştirildi

    def make_rounded_image(self, image_path, size):
        """Bir görüntüyü yuvarlak hale getirir."""
        image = Image.open(image_path).resize(size, Image.Resampling.LANCZOS)
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        rounded_image = Image.new("RGBA", size)
        rounded_image.paste(image, (0, 0), mask)
        return rounded_image

    def change_profile_photo(self, event=None):
        """Profil fotoğrafını değiştirmek için bir dosya seçici açar."""
        file_path = filedialog.askopenfilename(
            title="Fotoğraf Seç",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        if file_path:
            base_dir = os.path.dirname(__file__)
            save_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "profile_photo.png"))
            Image.open(file_path).save(save_path)
            self.update_profile_photo()  # Fotoğrafı güncelle

    def update_profile_photo(self):
        """Profil fotoğrafını günceller."""
        try:
            base_dir = os.path.dirname(__file__)
            photo_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "profile_photo.png"))
            photo = self.make_rounded_image(photo_path, (150, 150))  # Fotoğraf boyutu büyütüldü
            self.photo_label.configure(image=photo)
            self.photo_label.image = photo  # Referansı sakla
        except FileNotFoundError:
            print("Profil fotoğrafı bulunamadı!")