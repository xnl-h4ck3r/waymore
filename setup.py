#!/usr/bin/env python
import os
import shutil
from setuptools import setup, find_packages

target_directory = (
                os.path.join(os.getenv('APPDATA', ''), 'waymore') if os.name == 'nt'
                else os.path.join(os.path.expanduser("~"), ".config", "waymore") if os.name == 'posix'
                else os.path.join(os.path.expanduser("~"), "Library", "Application Support", "waymore") if os.name == 'darwin'
                else None
            )

# Copy the config.yml file to the target directory if it exists
configNew = False
if target_directory and os.path.isfile("config.yml"):
    os.makedirs(target_directory, exist_ok=True)
    # If file already exists, create a new one
    if os.path.isfile(target_directory+'/config.yml'):
        configNew = True
        os.rename(target_directory+'/config.yml',target_directory+'/config.yml.OLD')
        shutil.copy("config.yml", target_directory)
        os.rename(target_directory+'/config.yml',target_directory+'/config.yml.NEW')
        os.rename(target_directory+'/config.yml.OLD',target_directory+'/config.yml')
    else:
        shutil.copy("config.yml", target_directory)

setup(
    name="waymore",
    packages=find_packages(),
    version=__import__('waymore').__version__,
    description="Find way more from the Wayback Machine, Common Crawl, Alien Vault OTX, URLScan & VirusTotal!",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author="@xnl-h4ck3r",
    url="https://github.com/xnl-h4ck3r/waymore",
    py_modules=["waymore"],
    install_requires=["requests","pyyaml","termcolor","psutil","urlparse3","tldextract"],
    entry_points={
        'console_scripts': [
            'waymore = waymore.waymore:main',
        ],
    },
)

if configNew:
    print('\n\033[33mIMPORTANT: The file '+target_directory+'/config.yml already exists.\nCreating config.yml.NEW but leaving existing config.\nIf you need the new file, then remove the current one and rename config.yml.NEW to config.yml\n\033[0m')
else:
    print('\n\033[92mThe file '+target_directory+'/config.yml has been created.\n\033[0m')