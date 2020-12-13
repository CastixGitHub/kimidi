# This file is part of KiMidi.

# KiMidi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# KiMidi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with KiMidi.  If not, see <https://www.gnu.org/licenses/>.
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
            available_width=None,
            force_rows=None,
            force_cols=None,
            **kwargs
    ):
        # draw text: name of the panel. must be done before super
        self.name = self._name = name
        if '.' in name:
            self._name = name.split('.')[-1]
        self.name_label = CoreLabel(text=self._name, font_size=16)
        self.name_label.refresh()
        self.name_label = self.name_label.texture
        if available_width:
            self.width = available_width
        super().__init__(**kwargs)

        for item in items:
            self.add_widget(item)

        self.size_hint_min = (200, 20)
        self.size_hint_max = (Window.width, Window.height)

        # basic autodetect of cols/rows. self.size is not still available
        # rows can exceed height of the window
        child_width = sum(
            max(w.width, self.size_hint_min_x) for w in self.children
        ) or self.size_hint_max_x  # wontfix: + padding + spacing
        Logger.debug('kimidi.namedpanel: child_size %s on %s', child_width, self)
        # for w in self.children:
        #     print(w, w.size)

        self.rows = int(1 + (child_width / (available_width or Window.width)))
        Logger.debug('kimidi.namedpanel: detected %s rows on %s', self.rows, self)
        self.cols = int(len(items) / self.rows) or 1
        Logger.debug('kimidi.namedpanel: detected %s cols on %s', self.cols, self)

        if force_rows:
            self.rows = force_rows
            Logger.debug('kimidi.namedpanel: forced rows of %s (%s)', self, self.rows)
        if force_cols:
            self.cols = force_cols
            Logger.debug('kimidi.namedpanel: forced columns of %s (%s)', self, self.cols)

        while len(self.children) > self.rows * self.cols:
            Logger.warning('kimidi.namedpanel: adding 1 row to %s', self)
            self.rows += 1

    def __str__(self):
        return self.name
