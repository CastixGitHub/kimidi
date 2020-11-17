"""This module provides the user a fast way to manipulate controls already added to a panel."""  # noqa: disable=E902
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.settings import SettingsWithNoMenu
from kivy.logger import Logger
from settings import control
from widgets.namedpanel import NamedPanel


def _check_editable_mode_active():
    return True


def midieditable(func):
    """This decorator should be inserted in every midi widget where midi messages are supposed to be sent
    In order to provide a fast way to edit that control"""
    def _midieditable(*args, **kwargs):
        if not _check_editable_mode_active():
            func(*args, **kwargs)
        app = App.get_running_app()
        parent = args[0].parent
        try:
            while not isinstance(parent, NamedPanel):
                parent = parent.parent
        except AttributeError:
            Logger.error('kimidi.midieditable: cannot get parent of {args[0]}')
        panel = parent  # clarify following code
        print(app, parent)
        settings = SettingsWithNoMenu()
        settings.add_json_panel(
            'These settings are immediatly applied and saved, click outside to close',
            app.config,
            data=control.dumps_single(panel, args[0].name)
        )
        popup = Popup(
            title=f'Editing: {args[0]} on panel: {panel}',
            content=settings,
            size_hint=(.8, .8),
        )
        popup.open()
    return _midieditable
