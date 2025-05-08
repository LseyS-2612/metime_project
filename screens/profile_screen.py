import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageOps
from utils.data_manager import load_meditation_data, save_settings, load_settings
import os
from screens.settings_screen import SettingsScreen
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
        settings_btn.place(x=550, y=10)  # Sağ üst köşeye yerleştirildi

        # Kullanıcı fotoğrafı
        try:
            base_dir = os.path.dirname(__file__)
            photo_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "profile_photo.png"))
            photo = self.make_rounded_image(photo_path, (120, 120))  # Yuvarlak fotoğraf oluştur
            ctk_image = ctk.CTkImage(photo, size=(120, 120))  # CTkImage kullanımı
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
            font=("Helvetica", 18),
            text_color="#FFFFFF"
        )
        name_label.place(relx=0.5, rely=0.30, anchor="center")  # Fotoğrafın altına yerleştirildi

        # Streak bilgisi
        streak = load_meditation_data().get("streak", 0)
        streak_label = ctk.CTkLabel(
            self,
            text=f"Streak: 🔥 {streak}",
            font=("Helvetica", 18),
            text_color="#FFFFFF"
        )
        streak_label.place(relx=0.5, rely=0.35, anchor="center")  # İsmin altına yerleştirildi

        # Kullanıcı hakkında bilgi
        about_label = ctk.CTkLabel(
            self,
            text=f"Hakkımda: {settings.get('about', 'Meditasyon yapmayı seviyorum.')}",
            font=("Helvetica", 16),
            text_color="#FFFFFF",
            wraplength=400,
            justify="center"
        )
        about_label.place(relx=0.5, rely=0.40, anchor="center")  # Streak'in altına yerleştirildi

    def show_edit_screen(self):
        """Kullanıcı bilgilerini düzenleme ekranını gösterir."""
        for widget in self.winfo_children():
            widget.destroy()

        # Geri dönüş butonu
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",
            width=40,
            height=40,
            command=lambda: self.__init__(self.master, self.go_home),  # Profil ekranına geri dön
            fg_color="#212121",
            hover_color="#312e33"
        )
        back_btn.place(x=10, y=10)

        # Kullanıcı adı düzenleme
        name_entry = ctk.CTkEntry(
            self,
            placeholder_text="Adınızı girin",
            width=300,
            height=40
        )
        name_entry.insert(0, self.get_username())
        name_entry.place(relx=0.5, rely=0.3, anchor="center")

        # Hakkımda düzenleme
        about_entry = ctk.CTkEntry(
            self,
            placeholder_text="Hakkınızda bilgi girin",
            width=300,
            height=40
        )
        about_entry.insert(0, self.get_about())
        about_entry.place(relx=0.5, rely=0.4, anchor="center")

        # Tema seçimi
        theme_label = ctk.CTkLabel(
            self,
            text="Tema Seçin:",
            font=("Helvetica", 16),
            text_color="#FFFFFF"
        )
        theme_label.place(relx=0.5, rely=0.5, anchor="center")

        theme_option = ctk.CTkOptionMenu(
            self,
            values=["Purple & Gray", "Orange & Gray"],
            width=200,
            height=40
        )
        theme_option.set(self.get_theme())  # Varsayılan temayı ayarla
        theme_option.place(relx=0.5, rely=0.55, anchor="center")

        # Kaydet butonu
        save_btn = ctk.CTkButton(
            self,
            text="Kaydet",
            command=lambda: self.save_profile(name_entry.get(), about_entry.get(), theme_option.get()),
            width=150,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        save_btn.place(relx=0.5, rely=0.65, anchor="center")

    def save_profile(self, name, about, theme):
        """Kullanıcı bilgilerini ve temayı kaydeder."""
        settings = {"username": name, "about": about, "theme": theme}
        save_settings(settings)
        self.__init__(self.master, self.go_home)  # Profil ekranını yeniden yükle

    def get_username(self):
        """Kullanıcı adını ayarlardan alır."""
        settings = load_meditation_data()
        return settings.get("username", "John Doe")

    def get_about(self):
        """Hakkımda bilgisini ayarlardan alır."""
        settings = load_meditation_data()
        return settings.get("about", "Meditasyon yapmayı seviyorum.")

    def get_theme(self):
        """Temayı ayarlardan alır."""
        settings = load_meditation_data()
        return settings.get("theme", "Purple & Gray")

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
            photo = self.make_rounded_image(photo_path, (120, 120))  # Yuvarlak fotoğraf oluştur
            self.photo_label.configure(image=photo)
            self.photo_label.image = photo  # Referansı sakla
        except FileNotFoundError:
            print("Profil fotoğrafı bulunamadı!")

    def make_rounded_image(self, image_path, size):
        """Bir görüntüyü yuvarlak hale getirir."""
        image = Image.open(image_path).resize(size, Image.Resampling.LANCZOS)
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        rounded_image = Image.new("RGBA", size)
        rounded_image.paste(image, (0, 0), mask)
        return rounded_image