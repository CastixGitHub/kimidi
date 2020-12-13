from kivy.app import App
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.properties import NumericProperty, BoundedNumericProperty, ListProperty, StringProperty
from kivy.garden.knob import Knob

from modes import MidiCCAdapter
from modes.edit import prevent_when_edit


class Knob(Knob):
    scrolling_sensitivity = NumericProperty(0)

    def on_touch_down(self, touch):
        # TODO: send pull request upstream!
        if self.collide_point(*touch.pos):
            if not touch.is_mouse_scrolling:
                self.update_angle(touch)
            else:
                # they're logically inversed (natural scrolling)
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


class MidiKnob(Knob, MidiCCAdapter):
    control = BoundedNumericProperty(0, min=0, max=127)
    color = ListProperty(defaultvalue=[0, 0, 0, 0])
    name = StringProperty()
    text = StringProperty('n/a')
    label_pos = ListProperty(defaultvalue=[0, 0])

    def __init__(
            self,
            text,
            channel: int,
            control=1,
            color='#ff0000',
            minimum=0,
            maximum=127,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.output = App.get_running_app().cm.output
        self.name = text
        self.text = text
        self.channel = channel
        self.bind(pos=self.on_pos)

        self.control = control
        self.color = get_color_from_hex(color)
        self.size = (60, 60)
        self.min = minimum
        self.max = maximum
        self.step = 1
        self.value = 0
        self.knobimg_source = "libs/garden/garden.knob/img/ugly_knob.png"
        self.show_marker = True
        self.marker_color = [0, 1, 0, .5]
        self.scrolling_step = 4

    def on_pos(self, obj, pos):
        self.label_pos = [pos[0], pos[1] + obj.height]

    @prevent_when_edit
    def update_angle(self, touch):
        # override to prevent angle to be updated in edit mode
        super().update_angle(touch)

    @prevent_when_edit
    def on_touch_down(self, touch):
        super().on_touch_down(touch)

    def on_knob(self, value):
        self.cc(self.control, value)

    def __str__(self):
        return f'Knob: {self.name}'
