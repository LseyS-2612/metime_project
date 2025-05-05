import customtkinter as ctk
from utils.data_manager import load_settings, save_settings
import os

class SettingsScreen(ctk.CTkFrame):
    def __init__(self, master, go_back):
        super().__init__(master)

        self.go_back = go_back

        # Geri dönüş butonu
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",
            width=40,
            height=40,
            command=self.go_back,  # Geri dönüş fonksiyonu
            fg_color="#212121",
            hover_color="#312e33"
        )
        back_btn.place(x=10, y=10)

        self.name_entry = ctk.CTkEntry(
            self,
            placeholder_text="Adınızı girin",
            width=300,
            height=40
        )
        self.name_entry.insert(0, self.get_username())
        self.name_entry.place(relx=0.5, rely=0.25, anchor="center")

        # Hakkımda düzenleme
        about_label = ctk.CTkLabel(
            self,
            text="Hakkımda:",
            font=("Helvetica", 16),
            text_color="#FFFFFF"
        )
        about_label.place(relx=0.5, rely=0.35, anchor="center")

        self.about_entry = ctk.CTkEntry(
            self,
            placeholder_text="Hakkınızda bilgi girin",
            width=300,
            height=40
        )
        self.about_entry.insert(0, self.get_about())
        self.about_entry.place(relx=0.5, rely=0.4, anchor="center")

        # Tema seçimi
        theme_label = ctk.CTkLabel(
            self,
            text="Tema Seçin:",
            font=("Helvetica", 16),
            text_color="#FFFFFF"
        )
        theme_label.place(relx=0.5, rely=0.5, anchor="center")

        self.theme_option = ctk.CTkOptionMenu(
            self,
            values=["Purple & Gray", "Orange & Gray"],
            width=200,
            height=40
        )
        self.theme_option.set(self.get_theme())  # Varsayılan temayı ayarla
        self.theme_option.place(relx=0.5, rely=0.55, anchor="center")

        # Kaydet butonu
        save_btn_color = self.get_save_button_color()  # Temaya uygun renk al
        save_btn = ctk.CTkButton(
            self,
            text="Kaydet",
            command=self.save_settings,
            width=150,
            height=40,
            fg_color=save_btn_color["fg_color"],
            hover_color=save_btn_color["hover_color"]
        )
        save_btn.place(relx=0.5, rely=0.65, anchor="center")

    def save_settings(self):
        """Kullanıcı bilgilerini ve temayı kaydeder."""
        settings = {
            "username": self.name_entry.get(),
            "about": self.about_entry.get(),
            "theme": self.theme_option.get()
        }
        save_settings(settings)  # Ayarları kaydet

        # Temayı anında değiştir
        theme = settings["theme"]
        base_dir = os.path.dirname(__file__)
        if theme == "Purple & Gray":
            theme_path = os.path.join(base_dir, "..", "themes", "purple_gray_theme.json")
        elif theme == "Orange & Gray":
            theme_path = os.path.join(base_dir, "..", "themes", "orange_gray_theme.json")
        ctk.set_default_color_theme(theme_path)

        self.go_back()  # Geri dön

    def get_save_button_color(self):
        """Temaya uygun kaydet butonu renklerini döndürür."""
        theme = self.get_theme()
        if theme == "Purple & Gray":
            return {"fg_color": "#6A0DAD", "hover_color": "#40145C"}  # Mor tonları
        elif theme == "Orange & Gray":
            return {"fg_color": "#FF6A13", "hover_color": "#E85C04"}  # Turuncu tonları
        return {"fg_color": "#4CAF50", "hover_color": "#45A049"}  # Varsayılan yeşil

    def get_username(self):
        """Kullanıcı adını ayarlardan alır."""
        settings = load_settings()
        return settings.get("username", "John Doe")

    def get_about(self):
        """Hakkımda bilgisini ayarlardan alır."""
        settings = load_settings()
        return settings.get("about", "Meditasyon yapmayı seviyorum.")

    def get_theme(self):
        """Temayı ayarlardan alır."""
        settings = load_settings()
        return settings.get("theme", "Purple & Gray")