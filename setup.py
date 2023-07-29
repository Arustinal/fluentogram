# -*- coding: utf-8 -*-
from setuptools import setup

packages = [
    "fluentogram",
    "fluentogram.cli",
    "fluentogram.exceptions",
    "fluentogram.misc",
    "fluentogram.src",
    "fluentogram.src.abc",
    "fluentogram.src.impl",
    "fluentogram.src.impl.transformers",
    "fluentogram.tests",
    "fluentogram.typing_generator",
]

package_data = {"": ["*"]}

install_requires = ["fluent-compiler>=0.3,<0.4"]

entry_points = {"console_scripts": ["i18n = fluentogram.cli:cli"]}

setup_kwargs = {
    "name": "fluentogram",
    "version": "1.1.6",
    "description": "A proper way to use an i18n mechanism with Aiogram3.",
    "long_description": None,
    "author": "Aleks",
    "author_email": None,
    "maintainer": None,
    "maintainer_email": None,
    "url": "https://github.com/Arustinal/fluentogram",
    "packages": packages,
    "package_data": package_data,
    "install_requires": install_requires,
    "entry_points": entry_points,
    "python_requires": ">=3.9,<4.0",
}

setup(**setup_kwargs)
