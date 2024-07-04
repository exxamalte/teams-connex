import os

from setuptools import find_packages, setup

NAME = "teams_bridge"
AUTHOR = "Malte Franken"
AUTHOR_EMAIL = "coding@subspace.de"
DESCRIPTION = "Bridge between Teams and Home Assistant"
URL = "TBD"

REQUIRES = [
    "websockets>=12.0",
    "rumps>=0.4.0",
    "ruamel.yaml>=0.18.6",
    "httpx>=0.27.0",
    "expiringdict>=1.2.2",
    "platformdirs>=4.2.2",
    "pyinstaller>=6.8.0"
]


with open("README.md", "r") as fh:
    long_description = fh.read()

HERE = os.path.abspath(os.path.dirname(__file__))
VERSION = {}
with open(os.path.join(HERE, NAME, "__version__.py")) as f:
    exec(f.read(), VERSION)  # pylint: disable=exec-used

setup(
    name=NAME,
    version=VERSION["__version__"],
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
