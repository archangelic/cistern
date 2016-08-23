# cistern
Command line tool for downloading torrents from RSS feeds.

## Installation
```
pip install cistern
```
or
```
$ git clone https://github.com/archangelic/cistern
$ cd cistern
$ python setup.py install
```

## Usage
### Setting up Transmission
Before you run `cistern` you need to set up the connection to Transmission:
```
$ cistern setup
```
This will prompt you for the url, and port of your Transmission remote connection, as well as if it requires username and password.

### Adding Feeds
Once you are done setting up the connection to Transmission, you will need to add your first feed:
```
$ cistern add-feed
```
This will take you through some steps to set up the feed. It will ask you to give it a name, give the url, and it will give the option to supply a custom download directory for this feed.  

Optionally, you can supply these values with options:
```
$ cistern add-feed --name "Test RSS" --url "http://example.com/feed.rss" --download-dir /absolute/path/to/directory
```
`--name` and `--url` are required to create the feed entry. If no `--download-dir` is supplied, torrents from that feed will be downloaded to Transmission's default download directory.
 
### Running Cistern
At this point, you are ready to run cistern. Running `cistern` by itself will initiate a refresh of all feeds and add all previously undownloaded torrents to Transmission
 
### Listing Feeds and Torrents
Cistern's list command can list all the feeds or torrents it has. It takes one argument of either `feeds` or `torrents`.
You can use this command to get IDs for the `enable-feed` or `disable-feed` commands.
```
$ citern list feeds
  ID  Name      URL                          Download Directory           Enabled
----  --------  ---------------------------  ---------------------------  ---------
   1  Test RSS  http://example.com/feed.rss  /absolute/path/to/directory  Yes
```
 
### Enabling and Disabling Feeds
If you know the ID to your RSS feed, you can choose to enable it or disable it using the `disable-feed` or `enable-feed` commands.
```
$ cistern disable-feed 1
Test RSS disabled!

$ cistern enable-feed 1
Test RSS enabled!
```

### Refreshing feeds
If you want to just read the feeds to refresh the cache of torrents, simply run this command
```
$ cistern refresh
```
