import datetime
import os

from playhouse.migrate import *

def update():
    cistern_folder = os.getenv('CISTERNHOME', os.path.join(os.environ['HOME'], '.cistern'))
    db = SqliteDatabase(os.path.join(cistern_folder, 'cistern.db'))
    migrator = SqliteMigrator(db)

    date_added = DateTimeField(default=datetime.datetime.now)

    migrate(
        migrator.add_column('torrent', 'date_added', date_added)
    )
