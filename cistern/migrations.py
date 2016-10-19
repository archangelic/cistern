import os

from playhouse.migrate import *

cistern_folder = os.getenv('CISTERNHOME', os.path.join(os.environ['HOME'], '.cistern'))
db = SqliteDatabase(os.path.join(cistern_folder, 'cistern.db'))
migrator = SqliteMigrator(db)

date_added = DateTimeField(default=None)

migrate(
    migrator.add_column('torrent', 'date_added', date_added)
)
