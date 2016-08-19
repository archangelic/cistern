#!/usr/bin/env python3

import datetime
import os

import click
from configobj import ConfigObj
import feedparser
from peewee import *
from tabulate import tabulate
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
    url = CharField(unique=True)
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


# Other
def refresh_feed(feed, downloaded=False):
    feed_data = feedparser.parse(feed.url)
    click.echo("Refreshing feed: " + feed.name)
    with click.progressbar(feed_data.entries) as entries:
        for entry in entries:
            try:
                torrent = Torrent(
                    name=entry['title'],
                    url=entry[feed.tag],
                    feed=feed,
                    downloaded=downloaded
                )
                torrent.save()
            except IntegrityError:
                continue


# COMMAND LINE
@click.group()
def cli():
    pass


@cli.command('add-feed')
@click.option('--name', prompt=True)
@click.option('--url', callback=validate_url, prompt=True)
@click.option('--directory', default=None)
def add_feed(name, url, directory):
    tag = ''
    magnet = ''
    torrent = ''
    feed_data = feedparser.parse(url)
    entries = feed_data.entries
    e = entries[0]
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
        if click.confirm("Would you like to set a download directory for this feed?"):
            directory = click.prompt("Enter absolute path to directory")

    if directory and tag:
        feed = Feed(name=name, url=url, tag=tag, download_dir=directory)
        feed.save()
    elif tag:
        feed = Feed(name=name, url=url, tag=tag)
        feed.save()

    if click.confirm("Mark all entries as downloaded?"):
        refresh_feed(feed, downloaded=True)
    else:
        refresh_feed(feed)


@cli.command()
def refresh():
    for feed in Feed.select():
        refresh_feed(feed)


@cli.command('list')
@click.argument('list_type')
def lister(list_type):
    list_type = list_type.lower().strip()
    if list_type == 'feeds':
        feeds = Feed.select()
        feed_list = []
        for feed in feeds:
            if feed.enabled:
                enabled = 'Yes'
            else:
                enabled = "No"
            feed_list.append([feed.id, feed.name, feed.url, enabled])
        tab = tabulate(
            feed_list,
            ['ID', 'Name', 'URL', 'Enabled']
        )
        click.echo(tab)
    elif list_type == 'torrents':
        torrents = Torrent.select()
        torrent_list = []
        for torrent in torrents:
            if torrent.downloaded:
                downloaded = 'Yes'
            else:
                downloaded = 'No'
            torrent_list.append([torrent.id, torrent.name, torrent.feed.name, downloaded])
        tab = tabulate(
            torrent_list,
            ['ID', 'Name', 'Feed', 'Downloaded']
        )
        click.echo(tab)
    else:
        raise click.BadParameter("Please choose 'feeds' or 'torrents'")


if __name__ == '__main__':
    cli()
