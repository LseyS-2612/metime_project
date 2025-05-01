import customtkinter as ctk
from utils.data_manager import load_settings, save_settings

class SettingsScreen(ctk.CTkFrame):
    def __init__(self, master, go_home):
        super().__init__(master)

        self.go_home = go_home
        self.settings = load_settings()

        ctk.CTkLabel(self, text="⚙️ Ayarlar", font=("Arial", 22, "bold")).pack(pady=20)

        # Tema seçimi
        ctk.CTkLabel(self, text="Tema Seç:", font=("Arial", 14)).pack(pady=10)

        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "dark"))
        theme_menu = ctk.CTkOptionMenu(self, variable=self.theme_var, values=["light", "dark"])
        theme_menu.pack()

        # Kullanıcı adı
        ctk.CTkLabel(self, text="Adınız:", font=("Arial", 14)).pack(pady=10)
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.insert(0, self.settings.get("username", "Kullanıcı"))
        self.username_entry.pack()

        # Kaydet butonu
        save_btn = ctk.CTkButton(self, text="💾 Kaydet", command=self.save_and_apply)
        save_btn.pack(pady=20)

        # Geri dön
        back_btn = ctk.CTkButton(self, text="⬅️ Ana Sayfa", command=go_home)
        back_btn.pack(pady=10)

    def save_and_apply(self):
        # Güncel ayarları kaydet
        new_settings = {
            "theme": self.theme_var.get(),
            "username": self.username_entry.get()
        }
        save_settings(new_settings)

        # Tema anlık olarak uygula
        ctk.set_appearance_mode(new_settings["theme"])
