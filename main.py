import customtkinter
def button_callback():
    print("Butona Tıklandı")
    
app =customtkinter.CTk()
app.geometry("400x150")

button =customtkinter.CTkButton(app,text="My Button",command=button_callback,text_color="#2596be")
button.pack(padx=20,pady=20)

app.mainloop()