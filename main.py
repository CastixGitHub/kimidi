import os
import json
from functools import partial
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.slider import Slider
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.graphics import PushMatrix, PopMatrix
from kivy.graphics.context_instructions import Rotate
from kivy.properties import NumericProperty, BoundedNumericProperty, ListProperty, StringProperty
from kivy.garden.knob import Knob
from mido import Message, open_output


base_alpha = .8
colors = {
    'red': [1, 0, 0, base_alpha],
    'blue': [0, 1, 1, base_alpha],
    'green': [0, 0, 1, base_alpha],
    'cyan': [0, 1, 1, base_alpha],
    'magenta': [1, 0, 1, base_alpha],
    'l_green': [0xB6 / 255, 0xDC / 255, 0xE1 / 255, base_alpha],
    'l_grey': [0xD2 / 255, 0xE9 / 255, 0xE1 / 255, base_alpha],
    'l_sand': [0xFB / 255, 0xED / 255, 0xC9 / 255, base_alpha],
    'l_orange': [0xF8 / 255, 0xDD / 255, 0xA9 / 255, base_alpha],
    'l_red': [0xFC / 255, 0xB6 / 255, 0xD0 / 255, base_alpha],
    'l_pink': [0xFF / 255, 0xDE / 255, 0xE1 / 255, base_alpha],
}

def get_color(c):
    if isinstance(c, str):
        if c in colors:
            return colors[c]
        if c.startswith('#'):
            r = int(c[1:3], 16) / 255
            g = int(c[3:5], 16) / 255
            b = int(c[5:7], 16) / 255
            # TODO: handle rgba
            return [r, g, b, base_alpha]
    return c  # whatever it is...

def hex(l):
    s = '#'
    for c in l:
        s += format(int(c * 255), '02x')
    return s

def nof(n, of):
    """number of (3, 5) -> 5, 5, 5"""
    return [of for x in range(n)]


def parse_vkeybdmap(path):
    """If you wish you can share the same keyboard mapping of vkeyboard.
    This works even without vkeybdmap installed. but you should take care of locale"""
    available_keys = {}
    locations = [
        path,  # by default ~/.vkeybdmap
        '~/vkeybdmap',
        '/etc/vkeybdmap',
        '/usr/share/vkeybd/vkeybdmap',
        __file__.replace('main.py', '/vkeybdmap'),
    ]
    for path in locations:
        try:
            with open(path, 'r') as f:
                content = f.read()
                content = content[content.index('{') + 2:content.rindex('}') - 1]
                for line in content.split('\n'):
                    c = line[line.index('{') + 1:line.rindex(' ')]
                    v = int(line[line.rindex(' ') + 1:line.index('}')])
                    available_keys[c] = v
                return available_keys
        except FileNotFoundError:
            print('info:', path, 'not found')
    raise Exception('no vkeybdmap file found!')


output = open_output()

with open('config.json') as cfg_file:
    config = json.load(cfg_file)


keys = parse_vkeybdmap(config.get('vkeydbmap', '~/.vkeybdmap'))


class Knob(Knob):
    scrolling_sensitivity = NumericProperty(0)

    def on_touch_down(self, touch):
        # TODO: send pull request upstream!
        if self.collide_point(*touch.pos):
            if not touch.is_mouse_scrolling:
                self.update_angle(touch)
            else:
                # they're logacally inversed
                value = self.value
                if touch.button == 'scrolldown':
                    value += self.step * self.scrolling_step
                    if value > self.max:
                        value = self.max
                elif touch.button == 'scrollup':
                    value -= self.step * self.scrolling_step
                    if value < self.min:
                        value = self.min
                self.value = value  # call on_knob only once


Builder.load_string("""
<MidiKnob>:
    canvas:
        Color:
            rgba: self.color
        Ellipse:
            # considering width only because it's a circle, not an ellipse
            pos: [p + self.width / 4 for p in self.pos]
            size: [s - self.width / 2 for s in self.size]
    Label:
        pos: root.label_pos
        size: self.texture_size
        text: root.text
""", filename='MidiKnob.kv')


class MidiKnob(Knob):
    control = BoundedNumericProperty(0, min=0, max=127)
    color = ListProperty(defaultvalue=[0, 0, 0, 0])
    text = StringProperty('n/a')
    label_pos = ListProperty(defaultvalue=[0, 0])

    def __init__(self, text, *args, **kwargs):
        super(MidiKnob, self).__init__(*args, **kwargs)
        self.text = text
        self.bind(pos=self.on_pos)

    def on_pos(self, obj, pos):
        self.label_pos = [pos[0] + obj.width + 15, pos[1] + obj.height / 2]

    def on_knob(self, value):
        value = int(value)
        msg = Message('control_change', control=self.control, channel=0, value=value)
        output.send(msg)
        print(msg)


class BoxKnob(GridLayout):
    cols = 6
    min_rows = 4
    padding = nof(4, 10)

    def __init__(self, knobs, *args, **kwargs):
        super(BoxKnob, self).__init__(*args, **kwargs)
        for knob in knobs:
            inner = BoxLayout(orientation='horizontal')
            k = MidiKnob(knob['text'])
            k.control = knob['control']
            k.color = get_color(knob.get('color', [0, 0, 0, 0]))
            k.size = (60, 60)
            k.min = 0
            k.max = knob.get('max', 127)
            k.step = 1
            k.value = 0
            k.knobimg_source = "img/ugly_knob.png"
            k.show_marker = True
            k.marker_color = [0, 1, 0, .5]
            k.scrolling_step = 4
            inner.add_widget(k)
            self.add_widget(inner)


class BoxSliders(BoxLayout):
    orientation = 'horizontal'
    padding = nof(4, 10)

    def __init__(self, sliders, *args, **kwargs):
        super(BoxSliders, self).__init__(*args, **kwargs)

        def __on_value(obj, value):
            msg = Message('control_change', value=int(value), control=obj.control, channel=0)
            output.send(msg)
            print(msg)

        for slider in sliders:
            inner = BoxLayout(orientation='vertical')
            s = Slider(
                range=(0, slider.get('max', 127)),
                value=slider.get('default', 100),
                value_track=True,
                value_track_color=[1, 0, 0, 1],
                value_track_width=4,
                orientation='vertical',
                background_width=0,
                padding=25,
                cursor_size=[0, 0],
            )
            s.control = slider['control']
            s.bind(value=__on_value)

            inner.add_widget(Label(
                text=f"[color={hex(get_color(slider.get('color', [1, 1, 1, 1])))}]{slider['text']}[/color]",
                size_hint=(1, 0.05),
                markup=True,
            ))
            inner.add_widget(s)
            self.add_widget(inner)

        

class Root(BoxLayout):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)

        knobs = BoxKnob(config['knobs'], size_hint=(0.7, 1))
        self.add_widget(knobs)

        sliders = BoxSliders(config['sliders'], size_hint=(0.3, 1))
        self.add_widget(sliders)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)
        self._keyboard = None

    def on_key_down(self, keyboard, keycode, text, modifiers):
        if text in keys:
            msg = Message('note_on', note=keys[text], velocity=64, channel=0)
            print(msg)
            output.send(msg)

    def on_key_up(self, key, scancode=None, codepoint=None, modifier=None, **kwargs):
        if scancode[1] in keys:
            msg = Message('note_off', note=keys[scancode[1]], velocity=64, channel=0)
            print(msg)
            output.send(msg)



class KiMidiApp(App):
    def build(self):
        return Root()


# turn down auto repeat of keyboard (otherwise you'll get a lot on note_on for a single note_off)
os.system('xset -r')


# otherwise right and middle click will show red dots...
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


if __name__ == '__main__':
    try:
        KiMidiApp().run()
    except KeyboardInterrupt:
        print('closing')


# bring back autorepeat
os.system('xset r')
