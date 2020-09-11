from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Line
from kivy.properties import BoundedNumericProperty
from mido import Message, open_output


output = open_output()


class Potentiometer(Widget):
    value = BoundedNumericProperty(defaultvalue=0, min=0, max=127)
    def __init__(self, control=0, name='optional', h=200, w=200, **kwargs):
        super(Potentiometer, self).__init__(**kwargs)
        self.control = control
        self.name = name
        self.height = h
        self.width = w

        with self.canvas.before:
            Color(1, 0, 0, .5, mode='rgba')
        with self.canvas:
            Line(ellipse=(self.x, self.y, self.width, self.height))
            Color(1, 0, 0, 1, mode='rgba')
            Line(points=(self.center_x, self.center_y, w, h))
            self.label = Label(
                text=self.label_text(),
                font_size=14,
                height=20,
                width=w,
                pos=(0, self.center_y)
            )

    def label_text(self):
        return f'{self.name}: {self.value}'

    # def on_touch_move(self, event):
    #     print(event.x, event.y)

    def on_touch_down(self, event):
        if event.is_mouse_scrolling:
            # they're logacally inversed
            if event.button == 'scrolldown' and self.value < 127:
                self.value += 1
            elif event.button == 'scrollup' and self.value > 0:
                self.value -= 1
        self.label.text = self.label_text()


class Root(GridLayout):
    cols = 4
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        self.add_widget(Potentiometer(control=0))



class KiMidiApp(App):
    def build(self):
        #Clock.schedule_interval(lambda root: None, 1.0 / 60.0)
        return Root()


# otherwise right and middle click will show red dots...
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


if __name__ == '__main__':
    KiMidiApp().run()
