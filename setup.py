#!/usr/bin/env python3
from setuptools import setup
import sys

if not sys.version_info[0] == 3:
    sys.exit("Sorry, Cistern only supports Python 3.")

setup(
    name="cistern",
    version="0.1.5",
    license="MIT",
    url="https://github.com/archangelic/cistern",
    description="Command line tool for downloading torrents from RSS feeds.",
    author="Michael Hancock",
    author_email="michaelhancock89@gmail.com",
    download_url=(
        "https://github.com/archangelic/cistern/archive/v0.1.5.tar.gz"
    ),
    install_requires=[
        'click',
        'configobj',
        'feedparser',
        'peewee',
        'tabulate',
        'transmissionrpc',
    ],
    entry_points={
        'console_scripts': [
            'cistern=cistern.cistern:cli',
        ]
    },
    packages=[
        'cistern',
    ],
    keywords=['torrent', 'rss', 'transmission'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
