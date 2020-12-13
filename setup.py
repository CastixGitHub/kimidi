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
    zip_safe=False
)
