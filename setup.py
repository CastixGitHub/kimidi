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
from setuptools import setup, find_packages


install_requires = [
    'mido',
    'kivy>=2.0.0',
    # 'kivy_garden.knob',  # it's a legacy flower, installed in libs/garden
    'IPython',
]

devpkgs = [
    'flake8>=3.8.3',
]

setup(
    name='KiMidi',
    version='0.0.1',
    description='the energy of midi (desktop application written with kivy)',
    author='castix',
    author_email='castix@autistici.org',
    url='',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={
        'dev': devpkgs,
    },
    dependency_links=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    zip_safe=False
)
