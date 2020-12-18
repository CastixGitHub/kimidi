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

"""This isn't a real mode, but it might become a full mode in the future"""
# pylint: disable=unused-variable
from functools import partial
import trio
from kivy.logger import Logger
from patches.ipython import ipython_worker


def enter_debug(app):
    Logger.debug('kimidi.modes.debug: DEBUG enabled')

    async def ipython_trio():
        def _wrapper():
            ipython_worker(
                # banner1='',  # I like it!
                banner2='''logs from the application still appear on the same terminal
but you can ignore them most of the time,
hit return to get a clean propt :)''',
                header='KiMidi',
                exit_msg='To kill kimidi you have to close the window, then type control+d and confirm with y',
                colors='neutral',
                simple_prompt=False,
            )
        await trio.sleep(0.5)  # wait app startup (this can be improved but it's enough for now)
        await trio.to_thread.run_sync(_wrapper)

    async def main():
        async with trio.open_nursery() as nursery:
            nursery.start_soon(ipython_trio)
            nursery.start_soon(partial(app.async_run, async_lib='trio'))

    trio.run(main)
