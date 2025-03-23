from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import g4f
import threading


class AI(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.padding = [20, 20]
        self.spacing = 10

        self.header = BoxLayout(size_hint=(1, 0.1))
        self.header.add_widget(Label(text='Physics AI', font_size=24, bold=True, color=(0, 0.7, 1, 1)))
        self.add_widget(self.header)

        self.request_layout = BoxLayout(size_hint=(1, 0.1))
        self.request = TextInput(hint_text='Ваш запрос...', multiline=False, size_hint=(0.8, 1))
        self.request_layout.add_widget(self.request)

        self.send = Button(text="Отправить", size_hint=(0.2, 1), background_color=(0, 0.7, 1, 1))
        self.send.bind(on_press=self.send_button)
        self.request_layout.add_widget(self.send)
        self.add_widget(self.request_layout)

        self.scroll_view = ScrollView(size_hint=(1, 0.7))
        self.label = Label(
            text="Здесь будет ответ ИИ",
            size_hint_y=None,
            markup=True,
            halign='left',
            valign='top',
            color=(0, 0, 0, 1),
            text_size=(Window.width - 40, None)  # Устанавливаем text_size
        )
        self.label.bind(texture_size=self.label.setter('size'))
        self.scroll_view.add_widget(self.label)
        self.add_widget(self.scroll_view)

        self.footer = BoxLayout(size_hint=(1, 0.1))
        self.footer.add_widget(Label(text='© 2025 Physics AI', color=(0.5, 0.5, 0.5, 1)))
        self.add_widget(self.footer)

        self.text_buffer = ""
        self.is_updating = False

    def send_button(self, instance):
        request = self.request.text
        self.label.text = "Обработка запроса..."
        self.send.disabled = True
        self.text_buffer = ""

        # Запускаем поток для обработки запроса
        threading.Thread(target=self.process_request, args=(request,), daemon=True).start()

    def process_request(self, request):
        try:
            response = g4f.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system",
                           "content": "Ты помощник, который отвечает только на вопросы по физике ЕГЭ. экзаменам, вопросы напрямую связанные с физиикой. Если это другая тема, отвечай так: Это тема не относится к физике, задайте другой вопрос."},
                          {"role": "user", "content": request}],
                stream=True
            )
            for chunk in response:
                if isinstance(chunk, str):
                    self.text_buffer += chunk
                    if not self.is_updating:
                        self.is_updating = True
                        Clock.schedule_interval(self.update_label, 0.1)
        except Exception as e:
            self.text_buffer = f"Произошла ошибка: {e}"
        finally:
            Clock.schedule_once(lambda dt: self.finish_update(), 0)

    def update_label(self, dt):
        """Обновляет текст в Label из буфера."""
        if self.text_buffer:
            self.label.text = self.text_buffer
            self.scroll_view.scroll_y = 0

    def finish_update(self):
        """Завершает обновление и разблокирует кнопку."""
        self.is_updating = False
        Clock.unschedule(self.update_label)
        self.send.disabled = False


class PhysicsAI(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        return AI()


if __name__ == '__main__':
    PhysicsAI().run()