
import customtkinter as ctk
import json
import os
import pygame
import time
import threading


SETTINGS_PATH = "settings.json"

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        return {"theme": "dark", "username": "Kullanıcı"}
    with open(SETTINGS_PATH, "r") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=4)

class MeditationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere ayarları
        self.title("Meditasyon Uygulaması")
        self.geometry("600x800")
        self.resizable(False, False)

        # Tema ayarı
        ctk.set_appearance_mode("dark")  # veya "light"
        ctk.set_default_color_theme("blue")  # mavi tema

        # Sayfa yerleştirme
        self.current_frame = None
        self.show_home()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_home(self):
        self.clear_frame()
        self.current_frame = HomeScreen(self, self.show_meditation, self.show_settings)
        self.current_frame.pack(fill="both", expand=True)

    def show_meditation(self, selected_minutes=5):
        self.clear_frame()
        self.current_frame = MeditationScreen(self, self.show_home, selected_minutes)
        self.current_frame.pack(fill="both", expand=True)

    def show_settings(self):
        self.clear_frame()
        self.current_frame = SettingsScreen(self, self.show_home)
        self.current_frame.pack(fill="both", expand=True)


class HomeScreen(ctk.CTkFrame):
    def __init__(self, master, go_meditation, go_settings):
        super().__init__(master)

        self.go_meditation = go_meditation

        # Başlık
        title = ctk.CTkLabel(self, text="🧘 Meditasyon Uygulaması", font=("Arial", 22, "bold"))
        title.pack(pady=20)

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
        self.go_meditation(selected)


class MeditationScreen(ctk.CTkFrame):
    def __init__(self, master, go_home, duration):
        super().__init__(master)
        self.master = master
        self.go_home = go_home
        self.duration = duration * 60  # dakikayı saniyeye çevir
        self.remaining = self.duration
        self.running = False
        self.paused = False
        self.audio_path = self.get_audio_path(duration)
        self.hide_slider_job = None  # Slider'ı gizleme işini takip etmek için

        # Ses motorunu başlat
        pygame.mixer.init()

        # Başlık
        ctk.CTkLabel(self, text=f"{duration} Dakikalık Meditasyon", font=("Arial", 22, "bold")).pack(pady=20)

        # Sayaç
        self.timer_label = ctk.CTkLabel(self, text=self.format_time(self.remaining), font=("Arial", 40))
        self.timer_label.pack(pady=10)

        # Başlat/Duraklat butonu
        self.start_pause_btn = ctk.CTkButton(self, text="▶️ Başlat", command=self.start_or_pause_meditation)
        self.start_pause_btn.pack(pady=10)

        # Geri butonu
        self.back_btn = ctk.CTkButton(self, text="⏹️ Bitir ve Dön", command=self.stop_and_return)
        self.back_btn.pack(pady=10)

        # Ses simgesi
        self.volume_icon = ctk.CTkLabel(self, text="🔊", font=("Arial", 24))
        self.volume_icon.place(x=10, y=100)  # Sol tarafa yerleştir

        # Ses seviyesi slider'ı için çerçeve
        self.volume_frame = ctk.CTkFrame(self, width=50, height=200)

        # Ses seviyesi slider'ı (dikey)
        self.volume_slider = ctk.CTkSlider(
            self.volume_frame,
            from_=0,
            to=1,
            number_of_steps=20,
            orientation="vertical",
            command=self.change_volume
        )
        self.volume_slider.set(0.5)  # Varsayılan orta seviye
        self.volume_slider.pack(pady=10)

        # Slider başlangıçta gizli
        self.volume_frame.place_forget()

        # Fare olayları
        self.volume_icon.bind("<Enter>", self.show_volume_slider)
        self.volume_icon.bind("<Leave>", self.hide_volume_slider_delayed)
        self.volume_frame.bind("<Enter>", self.show_volume_slider)
        self.volume_frame.bind("<Leave>", self.hide_volume_slider_delayed)
        self.volume_slider.bind("<Enter>", self.cancel_hide_slider)
        self.volume_slider.bind("<Leave>", self.hide_volume_slider_delayed)


        # Başlangıçta sesi ayarla
        pygame.mixer.music.set_volume(0.5)

    def show_volume_slider(self, event=None):
        """Slider'ı göster."""
        if self.hide_slider_job:
            self.after_cancel(self.hide_slider_job)  # Gizleme işlemini iptal et
            self.hide_slider_job = None
        self.volume_frame.place(x=10, y=130)  # Ses simgesinin hemen altına yerleştir

    def hide_volume_slider_delayed(self, event=None):
        """Slider'ı gecikmeli olarak gizle."""
        self.hide_slider_job = self.after(300, self.hide_volume_slider)  # 300ms gecikme

    def hide_volume_slider(self, event=None):
        """Slider'ı gizle."""
        self.volume_frame.place_forget()
        self.hide_slider_job = None

    def cancel_hide_slider(self, event=None):
        """Slider'ın gizlenmesini iptal et."""
        if self.hide_slider_job:
            self.after_cancel(self.hide_slider_job)
            self.hide_slider_job = None

    def change_volume(self, value):
        """Ses seviyesini değiştir."""
        pygame.mixer.music.set_volume(float(value))

    def start_or_pause_meditation(self):
        if not self.running:
            # Meditasyonu başlat
            self.running = True
            self.paused = False
            self.start_pause_btn.configure(text="⏸️ Duraklat")  # Buton metnini 'Duraklat' olarak değiştir
            if not pygame.mixer.music.get_busy():  # Eğer müzik çalmıyorsa
                if self.audio_path:
                    pygame.mixer.music.load(self.audio_path)
                    pygame.mixer.music.play(start=self.duration - self.remaining)  # Kaldığı yerden başlat
                else:
                    ctk.CTkLabel(self, text="⚠️ Ses dosyası bulunamadı!", font=("Arial", 14, "bold"), fg_color="red").pack(pady=10)
                    return
            else:
                pygame.mixer.music.unpause()  # Müzik devam etsin
            threading.Thread(target=self.run_timer, daemon=True).start()  # Timer thread'i başlat
        elif self.paused:
            # Duraklatıldıysa devam et
            self.paused = False
            self.start_pause_btn.configure(text="⏸️ Duraklat")  # Buton metnini 'Duraklat' olarak değiştir
            pygame.mixer.music.unpause()  # Müzik devam etsin
        else:
            # Devam ediyorsa duraklat
            self.paused = True
            self.start_pause_btn.configure(text="▶️ Devam Et")  # Buton metnini 'Devam Et' olarak değiştir
            pygame.mixer.music.pause()  # Müzik duraksasın
            self.pause_timer()  # Sayaç duraklatılacak

    def pause_timer(self):
        # Timer'ı duraklat
        self.running = False

    def resume_timer(self):
        # Timer'ı devam ettir
        self.running = True
        threading.Thread(target=self.run_timer, daemon=True).start()

    def run_timer(self):
        while self.remaining > 0 and self.running:
            time.sleep(1)
            if not self.paused:
                self.remaining -= 1
            self.timer_label.configure(text=self.format_time(self.remaining))

        if self.remaining <= 0:
            self.end_session()

    def get_audio_path(self, minutes):
        audio_dir = "audio"
        filename = f"audio_{minutes}min.mp3"
        full_path = os.path.join(audio_dir, filename)
        if os.path.exists(full_path):
            return full_path
        else:
            return None  # yoksa uyarı verebiliriz

    def format_time(self, seconds):
        m, s = divmod(seconds, 60)
        return f"{int(m):02}:{int(s):02}"

    def end_session(self):
        self.running = False
        pygame.mixer.music.stop()
        self.timer_label.configure(text="⏳ Süre Bitti")

    def stop_and_return(self):
        self.running = False
        pygame.mixer.music.stop()
        self.go_home()


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


if __name__ == "__main__":
    app = MeditationApp()
    app.mainloop()
    settings = load_settings()
    ctk.set_appearance_mode(settings.get("theme", "dark"))