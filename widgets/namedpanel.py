"""module of the namedpanel widget, it is a panel with a border and a label on a corner"""
# pylint: disable=too-few-public-methods
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import Label as CoreLabel
from kivy.properties import ListProperty


Builder.load_string("""
<NamedPanel>:
    padding: [10, 25, 10, 10]
    spacing: [5, 5]
    canvas.before:
        Color:
            rgba: self.border_color
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, 15]
            width: 2
        Color:
            rgba: self.name_color
        Rectangle:
            size: self.name_label.size
            pos: [self.pos[0] + 10, self.pos[1] + self.height - 25]
            texture: self.name_label
""", filename='NamedPanel.kv')


class NamedPanel(GridLayout):
    name = None
    name_label = None
    border_color = ListProperty(defaultvalue=[1, 1, 1, 1])
    name_color = ListProperty(default_value=[1, 1, 1, 1])

    def __init__(
            self,
            name,
            items=None,
            available_width=1,
            force_rows=None,
            force_cols=None,
            **kwargs
    ):
        # draw text: name of the panel. must be done before super
        self.name = name
        self.name_label = CoreLabel(text=name, font_size=16)
        self.name_label.refresh()
        self.name_label = self.name_label.texture
        super().__init__(**kwargs)

        for item in items:
            self.add_widget(item)

        # basic autodetect of cols/rows. self.size is not still available
        # rows can exceed height of the window
        width = sum(w.width for w in self.children)  # + padding + spacing
        self.rows = int(1 + (width / (Window.width * available_width)))
        self.cols = int(1 + (len(items)) / self.rows)

        if force_rows:
            self.rows = force_rows
        if force_cols:
            self.cols = force_cols

        while len(self.children) > self.rows * self.cols:
            Logger.warning(f'adding 1 row to NamedPanel {name}')
            self.rows += 1

    def __str__(self):
        return self.name
