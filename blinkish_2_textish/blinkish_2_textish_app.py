import kivy
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

kivy.require('2.1.0')  # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label

FONT_SIZE = '18sp'


class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        Window.clearcolor = (1, 1, 1, 1)
        self.padding = (15, 15, 15, 15)
        self.color = (1, 1, 1, 1)
        self.orientation = 'vertical'
        self.morse_code_label = Label(text='Morse code', font_size=FONT_SIZE, size_hint=(None, 0.1),
                                      halign='left', color=(0, 0, 0, 1))
        self.add_widget(self.morse_code_label)
        self.current_code = TextInput(multiline=False, font_size=FONT_SIZE, size_hint=(1, 0.1))
        self.current_code.readonly = True
        self.add_widget(self.current_code)
        self.output_text = Label(text='Text output', font_size=FONT_SIZE, size_hint=(None, 0.1),
                                 halign='left', color=(0, 0, 0, 1))
        self.add_widget(self.output_text)
        self.text_output = TextInput(multiline=True, font_size=FONT_SIZE, size_hint=(1, 0.7))
        self.text_output.readonly = True
        self.add_widget(self.text_output)


class BlinkishToTextish(App):

    def build(self):
        return MainWidget()


if __name__ == '__main__':
    BlinkishToTextish().run()
