#!/usr/bin/env python3

import os

import click
from configobj import ConfigObj
import feedparser
from peewee import *
from tabulate import tabulate
import transmissionrpc

cistern_folder = os.path.join(os.environ['HOME'], '.cistern')
db = SqliteDatabase(os.path.join(cistern_folder, 'cistern.db'))


# MODELS
class Feed(Model):
    name = CharField()
    url = CharField()
    download_dir = CharField(default='')
    tag = CharField()
    enabled = BooleanField(default=True)

    class Meta:
        database = db

    def enable(self):
        self.enabled = True
        self.save()

    def disable(self):
        self.enabled = False
        self.save()


class Torrent(Model):
    name = CharField()
    url = CharField(unique=True)
    feed = ForeignKeyField(Feed, related_name='torrents')
    downloaded = BooleanField(default=False)

    class Meta:
        database = db

    def set_downloaded(self):
        self.downloaded = True
        self.save()

# Connection to Database and set up files
if not os.path.isdir(cistern_folder):
    os.mkdir(cistern_folder)

if not os.path.isfile(os.path.join(cistern_folder, 'cistern.db')):
    db.connect()
    db.create_tables([Feed, Torrent])
elif os.path.isfile(os.path.join(cistern_folder, 'cistern.db')):
    db.connect()

config = ConfigObj(os.path.join(cistern_folder, 'config'))


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


def cistern():
    if config['require_auth']:
        tremote = transmissionrpc.Client(
            address=config['url'],
            port=int(config['port']),
            user=config['username'],
            password=config['password']
        )
    else:
        tremote = transmissionrpc.Client(
            address=config['url'],
            port=int(config['port'])
        )
    click.clear()
    for feed in Feed.select().where(Feed.enabled == True):
        refresh_feed(feed)
        click.echo('Downloading torrents:')
        torrent_list = feed.torrents.select().where(Torrent.downloaded == False)
        if torrent_list:
            with click.progressbar(torrent_list) as torrents:
                transmission_args = {}
                if feed.download_dir:
                    transmission_args['download_dir'] = feed.download_dir
                for torrent in torrents:
                    tremote.add_torrent(torrent.url, **transmission_args)
                    torrent.set_downloaded()
        else:
            click.echo("No torrents to download in this feed")


# COMMAND LINE
@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        cistern()
    else:
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


@cli.command()
def setup():
    click.clear()
    click.echo('Welcome to Cistern\n\n')
    click.echo("Transmission Information")
    config['url'] = click.prompt("URL", default='localhost')
    config['port'] = click.prompt("Port", default=9091)
    if click.confirm("Requires username and password?"):
        config['require_auth'] = True
        config['username'] = click.prompt("Username")
        config['password'] = click.prompt("Password")
    else:
        config['require_auth'] = False
        config['username'] = ''
        config['password'] = ''
    config.write()
    click.clear()
    click.echo("Successfully set up!\nUse the 'add-feed' command to add your first RSS feed.")


@cli.command('disable-feed')
@click.argument('feed_id')
def disable_feed(feed_id):
    try:
        int(id)
    except ValueError:
        raise click.BadParameter('Please enter a valid feed id')
    feed = Feed.get(Feed.id == feed_id)
    if feed:
        if feed.enabled:
            feed.disable()
            click.echo(feed.name + " disabled!")
        else:
            click.echo(feed.name + ' is already disabled!')
    else:
        click.echo('Please enter a valid feed id')


@cli.command('enable-feed')
@click.argument('feed_id')
def enable_feed(feed_id):
    try:
        int(id)
    except ValueError:
        raise click.BadParameter('Please enter a valid feed id')
    feed = Feed.get(Feed.id == feed_id)
    if feed:
        if not feed.enabled:
            feed.enable()
            click.echo(feed.name + " enabled!")
        else:
            click.echo(feed.name + ' is already enabled!')
    else:
        click.echo('Please enter a valid feed id')


if __name__ == '__main__':
    cli()
