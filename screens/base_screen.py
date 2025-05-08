from PIL import Image
import customtkinter as ctk
import os

class BaseScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Ortak arka plan resmi
        base_dir = os.path.dirname(__file__)
        background_path = os.path.abspath(os.path.join(base_dir, "..", "assets", "background.jpg"))
        if os.path.exists(background_path):
            bg_image = Image.open(background_path)
            self.bg_image = ctk.CTkImage(bg_image, size=(600, 800))  # CTkImage kullanımı

            # Arka plan resmi için bir CTkLabel
            bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)