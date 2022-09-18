#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="waymore",
    packages=find_packages(),
    version="1.8",
    description="Find way more from the Wayback Machine",
    long_description=open("README.md").read(),
    author="@xnl-h4ck3r",
    url="https://github.com/xnl-h4ck3r/waymore",
    py_modules=["waymore"],
    install_requires=["argparse","requests","pyyaml","termcolor","psutil","urlparse3"],
)