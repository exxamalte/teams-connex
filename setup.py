"""Setup of Teams Connex application."""

from setuptools import find_packages, setup

from teams_connex.__version__ import __version__

NAME = "teams_connex"
AUTHOR = "Malte Franken"
AUTHOR_EMAIL = "coding@subspace.de"
DESCRIPTION = "Connex between Teams and Home Assistant"
URL = "https://github.com/exxamalte/teams-connex"

REQUIRES = [
    "websockets>=12.0",
    "rumps>=0.4.0",
    "ruamel.yaml>=0.18.6",
    "httpx>=0.27.0",
    "expiringdict>=1.2.2",
    "platformdirs>=4.2.2",
    "pyinstaller>=6.9.0",
]


with open("README.md") as fh:
    long_description = fh.read()

setup(
    name=NAME,
    version=__version__,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    license="Apache-2.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(exclude=("tests",)),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS",
        "Topic :: Communications :: Conferencing",
        "Topic :: Home Automation",
    ],
    install_requires=REQUIRES,
)
