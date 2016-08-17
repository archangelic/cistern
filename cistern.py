#!/usr/bin/env python3

import datetime
import os

import click
from configobj import ConfigObj
import feedparser
from peewee import *
from validate import Validator

cistern_folder = os.path.join(os.environ['HOME'], '.cistern')
db = SqliteDatabase(os.path.join(cistern_folder, 'cistern.db'))


class Feed(Model):
    name = CharField(max_length=50)
    url = CharField(max_length=255)
    download_dir = CharField(max_length=255)
    last_checked = DateTimeField(default=datetime.datetime.now)
    enabled = BooleanField(default=True)

    class Meta:
        database = db


class Torrent(Model):
    name = CharField(max_length=40)
    url = CharField(max_length=255)
    feed = ForeignKeyField(Feed, related_name='torrents')

    class Meta:
        database = db

if not os.path.isdir(cistern_folder):
    os.mkdir(cistern_folder)

if not os.path.isfile(os.path.join(cistern_folder, 'cistern.db')):
    db.connect()
    db.create_tables([Feed])
elif os.path.isfile(os.path.join(cistern_folder, 'cistern.db')):
    db.connect()

click.clear()
click.echo("Hello World!")
click.echo(cistern_folder)
click.pause()
click.clear()
