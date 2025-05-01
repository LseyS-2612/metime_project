import customtkinter as ctk
from utils.data_manager import load_meditation_data, update_streak

class HomeScreen(ctk.CTkFrame):
    def __init__(self, master, go_meditation, go_settings):
        super().__init__(master)

        self.go_meditation = go_meditation

        # Başlık
        title = ctk.CTkLabel(self, text="🧘 Meditasyon Uygulaması", font=("Arial", 22, "bold"))
        title.pack(pady=20)

        # Streak bilgisi
        streak = load_meditation_data().get("streak", 0)
        streak_label = ctk.CTkLabel(self, text=f"🔥 Streak: {streak} gün", font=("Arial", 16))
        streak_label.pack(pady=10)

        # Açıklama
        info = ctk.CTkLabel(self, text="Kendine zaman ayırmak için bir süre seç ve başla.",
                            wraplength=300, justify="center", font=("Arial", 14))
        info.pack(pady=10)

        # Süre seçimi
        self.selected_time = ctk.IntVar(value=5)  # varsayılan 5 dakika

        time_frame = ctk.CTkFrame(self)
        time_frame.pack(pady=20)

        for minute in [5, 10, 15]:
            rb = ctk.CTkRadioButton(time_frame, text=f"{minute} dakika", variable=self.selected_time, value=minute)
            rb.pack(side="left", padx=10)

        # Başlat butonu
        start_btn = ctk.CTkButton(self, text="🕒 Meditasyona Başla", command=self.start_meditation)
        start_btn.pack(pady=20)

        # Ayarlar butonu
        settings_btn = ctk.CTkButton(self, text="⚙️ Ayarlar", command=go_settings)
        settings_btn.pack(pady=10)

    def start_meditation(self):
        selected = self.selected_time.get()
        update_streak()  # Streak'i güncelle
        self.go_meditation(selected)