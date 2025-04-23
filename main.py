from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget

class TodoApp(App):
    def build(self):
        self.tasks = []  # Yapılacaklar listesi
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Yapılacaklar başlık
        title_label = Label(text="Yapılacaklar Listesi", font_size=24, size_hint=(1, 0.1))
        self.layout.add_widget(title_label)

        # Yapılacak görev ekleme kısmı
        self.task_input = TextInput(hint_text="Yeni görev ekleyin", size_hint=(1, 0.1))
        self.layout.add_widget(self.task_input)

        # Görev ekleme butonu
        self.add_task_button = Button(text="Görev Ekle", size_hint=(1, 0.1))
        self.add_task_button.bind(on_press=self.add_task)
        self.layout.add_widget(self.add_task_button)

        # Görevlerin listeleneceği alan
        self.task_list = ScrollView(size_hint=(1, 0.7))
        self.task_grid = GridLayout(cols=1, padding=10, size_hint_y=None)
        self.task_grid.bind(minimum_height=self.task_grid.setter('height'))
        self.task_list.add_widget(self.task_grid)
        self.layout.add_widget(self.task_list)

        return self.layout

    def on_start(self):
        # Uygulamanın başlığını ayarlama
        self.title = "Yapılacaklar Listesi"

    def add_task(self, instance):
        task_text = self.task_input.text.strip()  # Kullanıcının girdiği metni al
        if task_text:
            self.tasks.append(task_text)
            self.task_input.text = ""  # Input alanını temizle
            self.update_task_list()

    def update_task_list(self):
        # Listeyi güncelle
        self.task_grid.clear_widgets()  # Mevcut görevleri temizle
        for task in self.tasks:
            task_layout = BoxLayout(size_hint_y=None, height=40)
            checkbox = CheckBox(size_hint=(None, None), size=(40, 40))
            task_label = Label(text=task, size_hint_y=None, height=40)
            delete_button = Button(text="Sil", size_hint=(None, None), size=(60, 40))

            # Silme butonuna tıklama olayı
            delete_button.bind(on_press=lambda instance, task=task: self.delete_task(task))

            task_layout.add_widget(checkbox)
            task_layout.add_widget(task_label)
            task_layout.add_widget(delete_button)

            self.task_grid.add_widget(task_layout)

    def delete_task(self, task):
        # Görev silme
        self.tasks.remove(task)
        self.update_task_list()

if __name__ == "__main__":
    TodoApp().run()
