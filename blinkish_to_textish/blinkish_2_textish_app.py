import logging

import kivy
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput

from blinkish_to_textish import MorseCode, start_blink_detection, stop_blink_detection, Blink

kivy.require('2.1.0')  # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label

NORMAL_FONT_SIZE = '18sp'
LARGE_FONT_SIZE = '24sp'


class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.morse_code = ''
        self.converted_text = ''
        Window.clearcolor = (1, 1, 1, 1)
        self.top_panel = BoxLayout(orientation='vertical', size_hint=(1.0, 0.5))
        self.padding = (15, 15, 15, 15)
        self.color = (1, 1, 1, 1)
        self.orientation = 'vertical'
        self.add_widget(self.top_panel)

        self.morse_code_label = Label(text='Morse code', font_size=NORMAL_FONT_SIZE, size_hint=(None, 0.1),
                                      halign='left', color=(0, 0, 0, 1))
        self.top_panel.add_widget(self.morse_code_label)

        self.current_code = TextInput(multiline=False, font_size=NORMAL_FONT_SIZE, size_hint=(None, 0.1))
        self.current_code.readonly = True
        self.top_panel.add_widget(self.current_code)

        self.output_text = Label(text='Text output', font_size=NORMAL_FONT_SIZE, size_hint=(None, 0.1),
                                 halign='left', color=(0, 0, 0, 1))
        self.top_panel.add_widget(self.output_text)

        self.text_output = TextInput(multiline=True, font_size=NORMAL_FONT_SIZE, size_hint=(1.0, 0.7))
        self.text_output.readonly = True
        self.top_panel.add_widget(self.text_output)

        self.bottom_panel = GridLayout(size_hint=(1.0, 0.5), cols=6, rows=6)
        self.add_widget(self.bottom_panel)
        for name, member in MorseCode.__members__.items():
            if name.startswith('N_'):
                text = member.code + ' ' + name[2:]
            else:
                text = member.code + ' ' + name
            print('text: ' + text)
            self.bottom_panel.add_widget(Label(text=text, font_size=LARGE_FONT_SIZE, color=(0, 0, 0, 1)))

    def update_ui(self, dt):
        self.text_output.text = self.converted_text
        self.current_code.text = self.morse_code

    def blink_detected(self, blink, blink_length):
        print(str(blink) + ' with length: ' + str(blink_length))
        if blink == Blink.SHORT_BLINK:
            self.morse_code += '.'
        elif blink == Blink.LONG_BLINK:
            self.morse_code += '-'
        elif blink == Blink.PAUSE:
            try:
                char = MorseCode.get_character(self.morse_code)
                if char is not None:
                    self.converted_text = self.converted_text + char
                    print('Converted "' + self.morse_code + '" to ' + char + ' full text: "' + self.converted_text + '"')
                self.morse_code = ''
            except AttributeError as e:
                logging.critical(e, exc_info=True)
                print('Invalid Morse code: ' + self.morse_code)
                self.morse_code = ''
        elif blink == Blink.VERY_LONG_BLINK:
            self.morse_code = ''
            print('Morse code reseted')
        Clock.schedule_once(self.update_ui)


class BlinkishToTextishApp(App):

    def build(self):
        print('Creating widget')
        widget = MainWidget()
        print('Widget created')
        start_blink_detection(5000, widget.blink_detected, False)
        return widget

    def on_stop(self, *args):
        print('Window closing')
        stop_blink_detection()
        return True


if __name__ == '__main__':
    BlinkishToTextishApp().run()
