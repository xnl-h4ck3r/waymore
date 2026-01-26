#!/usr/bin/env python
import os
import re

from setuptools import find_packages, setup

# Read version from __init__.py without importing


def get_version():
    init_path = os.path.join(os.path.dirname(__file__), "waymore", "__init__.py")
    with open(init_path, encoding="utf-8") as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="waymore",
    packages=find_packages(),
    version=get_version(),
    description="Find way more from the Wayback Machine, Common Crawl, Alien Vault OTX, URLScan & VirusTotal!",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="@xnl-h4ck3r",
    url="https://github.com/xnl-h4ck3r/waymore",
    install_requires=[
        "requests",
        "pyyaml",
        "termcolor",
        "psutil",
        "urlparse3",
        "tldextract",
    ],
    entry_points={
        "console_scripts": [
            "waymore = waymore.waymore:main",
        ],
    },
)
