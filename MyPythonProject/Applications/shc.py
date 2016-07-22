# -*- coding: ISO-8859-1 -*-
import sqlite3
import datetime
from . import shared

__author__ = 'Xavier ROSSET'


conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
conn.cursor().execute("INSERT INTO discs (albumid, discid, tracks, created) values(?, ?, ?, ?)", ("S.Springsteen, Bruce.1.20141117.The Album Collection Vol 1 (1973-1984).3/7.1.19750000.1", "1", 8,
                                                                                                  datetime.datetime(2016, 2, 19, 18, 55, 45, 875670)))
# for i in conn.cursor().execute("SELECT * FROM albums WHERE rowid=?", (57,)):
#     print(i)
conn.commit()
conn.close()
