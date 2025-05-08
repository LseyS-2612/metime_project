import customtkinter as ctk
import json
import os
import random

class QuotesScreen(ctk.CTkFrame):
    def __init__(self, master, go_home):
        super().__init__(master)
        
        self.go_home = go_home
        
        # Arka plan rengi
        self.configure(fg_color="#2b2b2b")
        
        # Geri dönüş butonu
        back_btn = ctk.CTkButton(
            self,
            text="⬅️",
            width=40,
            height=40,
            command=self.go_home,  # Ana ekrana dönmek için
            fg_color="#212121",
            hover_color="#312e33"
        )
        back_btn.place(x=10, y=10)
        
        # Başlık
        title_label = ctk.CTkLabel(
            self,
            text="Motivasyon Alıntıları",
            font=("Helvetica", 24, "bold"),
            text_color="#FFFFFF"
        )
        title_label.place(relx=0.5, rely=0.1, anchor="center")
        
        # Alıntılar listesi için kaydırılabilir alan
        quotes_frame = ctk.CTkScrollableFrame(
            self,
            width=500,
            height=500,
            fg_color="#343434",
            corner_radius=10
        )
        quotes_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Alıntıları yükle
        quotes = self.load_quotes()
        
        # Alıntıları ekrana yerleştir
        for i, quote in enumerate(quotes):
            quote_text = quote.get("text", "")
            author = quote.get("author", "Bilinmeyen")
            
            quote_frame = ctk.CTkFrame(
                quotes_frame,
                fg_color="#424242",
                corner_radius=15,
                height=100
            )
            quote_frame.pack(fill="x", padx=10, pady=10, expand=True)
            
            quote_label = ctk.CTkLabel(
                quote_frame,
                text=f'"{quote_text}"',
                font=("Times New Roman", 16),
                wraplength=450,
                justify="left",
                text_color="#FFFFFF"
            )
            quote_label.pack(padx=15, pady=(15, 5), anchor="w")
            
            author_label = ctk.CTkLabel(
                quote_frame,
                text=f"- {author}",
                font=("Times New Roman", 14, "italic"),
                text_color="#AAAAAA"
            )
            author_label.pack(padx=15, pady=(0, 15), anchor="e")
        
        # Temaya göre buton renklerini belirle
        theme = self.get_current_theme()
        if theme == "Purple & Gray":
            button_colors = {"fg_color": "#521a78", "hover_color": "#3e135b"}  # Purple & Gray renkleri
        elif theme == "Orange & Gray":
            button_colors = {"fg_color": "#FF6A13", "hover_color": "#e65a00"}  # Orange & Gray renkleri
        else:
            button_colors = {"fg_color": "#424242", "hover_color": "#535353"}  # Varsayılan renkler

        # Favori alıntı eklemek için buton
        add_favorite_btn = ctk.CTkButton(
            self,
            text="Yeni Alıntı Ekle",
            width=150,
            height=40,
            command=self.show_add_quote_dialog,
            fg_color=button_colors["fg_color"],
            hover_color=button_colors["hover_color"]
        )
        add_favorite_btn.place(relx=0.5, rely=0.9, anchor="center")
    
    def load_quotes(self):
        """JSON dosyasından alıntıları yükler."""
        try:
            base_dir = os.path.dirname(__file__)
            file_path = os.path.abspath(os.path.join(base_dir, "..", "quotes.json"))
            
            with open(file_path, "r", encoding="utf-8") as file:
                quotes = json.load(file)
                # JSON yapısını dönüştür (quote -> text anahtarı)
                formatted_quotes = []
                for quote in quotes:
                    formatted_quotes.append({
                        "text": quote.get("quote", ""),
                        "author": quote.get("author", "Bilinmeyen")
                    })
                return formatted_quotes
        except FileNotFoundError:
            print("quotes.json dosyası bulunamadı!")
            return []
    
    def show_add_quote_dialog(self):
        """Yeni alıntı eklemek için dialog gösterir."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Yeni Alıntı Ekle")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Dialog içeriği
        ctk.CTkLabel(dialog, text="Alıntı:").place(x=20, y=20)
        quote_entry = ctk.CTkTextbox(dialog, width=360, height=100)
        quote_entry.place(x=20, y=50)
        
        ctk.CTkLabel(dialog, text="Yazar:").place(x=20, y=160)
        author_entry = ctk.CTkEntry(dialog, width=360)
        author_entry.place(x=20, y=190)
        
        # Kaydet butonu
        save_btn = ctk.CTkButton(
            dialog,
            text="Kaydet",
            command=lambda: self.save_quote(quote_entry.get("1.0", "end-1c"), author_entry.get(), dialog)
        )
        save_btn.place(x=150, y=250)
    
    def save_quote(self, quote_text, author, dialog):
        """Yeni alıntıyı kaydeder."""
        if not quote_text.strip():
            return
        
        try:
            base_dir = os.path.dirname(__file__)
            file_path = os.path.abspath(os.path.join(base_dir, "..", "quotes.json"))
            
            # Mevcut alıntıları yükle
            with open(file_path, "r", encoding="utf-8") as file:
                quotes = json.load(file)
            
            # Yeni alıntıyı ekle
            quotes.append({
                "text": quote_text,
                "author": author if author.strip() else "Bilinmeyen"
            })
            
            # Alıntıları kaydet
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(quotes, file, ensure_ascii=False, indent=4)
            
            dialog.destroy()
            
            # Ekranı yenile
            self.go_home()
            self.master.after(100, lambda: self.master.show_quotes_screen())
            
        except Exception as e:
            print(f"Alıntı kaydedilirken hata oluştu: {e}")
    def get_current_theme(self):
        """Geçerli temayı ayarlardan alır ve temaya göre renk döndürür."""
        base_dir = os.path.dirname(__file__)
        settings_path = os.path.abspath(os.path.join(base_dir, "..", "utils", "settings.json"))
        try:
            with open(settings_path, "r", encoding="utf-8") as file:
                settings = json.load(file)
                theme = settings.get("theme", "Purple & Gray")  # Varsayılan tema
                if theme == "Purple & Gray":
                    return {"theme": theme, "button_colors": {"fg_color": "#521a78", "hover_color": "#3e135b"}}
                elif theme == "Orange & Gray":
                    return {"theme": theme, "button_colors": {"fg_color": "#FF6A13", "hover_color": "#e65a00"}}
                else:
                    return {"theme": theme, "button_colors": {"fg_color": "#424242", "hover_color": "#535353"}}  # Varsayılan renkler
        except FileNotFoundError:
            return {"theme": "Purple & Gray", "button_colors": {"fg_color": "#521a78", "hover_color": "#3e135b"}}  # Varsayılan tema ve renkler