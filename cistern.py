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


# MODELS
class Feed(Model):
    name = CharField()
    url = CharField()
    download_dir = CharField(default='')
    last_checked = DateTimeField(default=datetime.datetime.now)
    tag = CharField()
    enabled = BooleanField(default=True)

    class Meta:
        database = db


class Torrent(Model):
    name = CharField()
    url = CharField()
    feed = ForeignKeyField(Feed, related_name='torrents')
    downloaded = BooleanField(default=False)

    class Meta:
        database = db

# Connection to Database
if not os.path.isdir(cistern_folder):
    os.mkdir(cistern_folder)

if not os.path.isfile(os.path.join(cistern_folder, 'cistern.db')):
    db.connect()
    db.create_tables([Feed, Torrent])
elif os.path.isfile(os.path.join(cistern_folder, 'cistern.db')):
    db.connect()


# VALIDATION
def validate_url(ctx, param, value):
    if not value.startswith(('http://', 'https://')):
        raise click.BadParameter("Please enter valid URL")
    else:
        return value


# COMMAND LINE
@click.group()
def cli():
    return True


@cli.command('add-feed')
@click.option('--name', prompt=True)
@click.option('--url', callback=validate_url, prompt=True)
@click.option('--directory', default=None)
def add_feed(name, url, directory):
    tag = ''
    magnet = ''
    torrent = ''
    feed_data = feedparser.parse(url)
    e = feed_data.entries[0]
    for each in e:
        try:
            if e[each].startswith('magnet:'):
                magnet = each
            elif e[each].endswith('.torrent'):
                torrent = each
        except AttributeError:
            continue

    if magnet:
        tag = magnet
    elif torrent:
        tag = torrent

    if not directory:
        if click.confirm("Would you like to set a download directory?"):
            directory = click.prompt("Enter absolute path to directory")

    if tag:
        if directory:
            feed = Feed(name=name, url=url, tag=tag, download_dir=directory)
            feed.save()
        else:
            feed = Feed(name=name, url=url, tag=tag)
            feed.save()


if __name__ == '__main__':
    cli()
