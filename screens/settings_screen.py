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
        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "Purple & Gray"))
        theme_menu = ctk.CTkOptionMenu(self, variable=self.theme_var, values=["Purple & Gray", "Orange & Gray"])
        theme_menu.pack(pady=10)

        # Kullanıcı adı
        ctk.CTkLabel(self, text="Adınız:", font=("Arial", 14)).pack(pady=10)
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.insert(0, self.settings.get("username", "Kullanıcı"))
        self.username_entry.pack(pady=10)

        # Kaydet butonu
        save_btn = ctk.CTkButton(self, text="💾 Kaydet", command=self.save_and_apply)
        save_btn.pack(pady=5)

        # Geri dön butonu (sadece ikon olarak sol üst köşeye taşındı)
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",  # Sadece ikon
            width=40,  # Buton genişliği
            height=40,  # Buton yüksekliği
            command=go_home
        )
        back_btn.place(x=5, y=5)  # Sol üst köşeye yerleştir

    def save_and_apply(self):
        # Güncel ayarları kaydet
        new_settings = {
            "theme": self.theme_var.get(),
            "username": self.username_entry.get()
        }
        save_settings(new_settings)

        # Tema anlık olarak uygula
        if new_settings["theme"] == "Purple & Gray":
            ctk.set_default_color_theme("C:/Users/klcan/metime_project/themes/purple_gray_theme.json")
        elif new_settings["theme"] == "Orange & Gray":
            ctk.set_default_color_theme("C:/Users/klcan/metime_project/themes/orange_gray_theme.json")
