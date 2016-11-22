# -*- coding: ISO-8859-1 -*-
import os
import sqlite3
import datetime
from Applications.shared import dateformat, TEMPLATE1, TEMPLATE2, TEMPLATE3, UTC, LOCAL

__author__ = 'Xavier ROSSET'


c = sqlite3.connect(os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), detect_types=sqlite3.PARSE_DECLTYPES)
c.row_factory = sqlite3.Row
with c:
    c.execute("CREATE TABLE IF NOT EXISTS mytable (id INTEGER PRIMARY KEY ASC AUTOINCREMENT, ts TIMESTAMP NOT NULL)")
    c.execute("INSERT INTO mytable (ts) VALUES (?)", (datetime.datetime.utcnow(),))
    for row in c.execute("SELECT id, ts FROM mytable ORDER BY id"):
        print("# ----- #")
        print(row["id"])
        if isinstance(row["ts"], datetime.datetime):
            print(dateformat(UTC.localize(row["ts"]), TEMPLATE1))
            print(dateformat(UTC.localize(row["ts"]).astimezone(LOCAL), TEMPLATE1))
            print(dateformat(UTC.localize(row["ts"]).astimezone(LOCAL), TEMPLATE2))
            print(dateformat(UTC.localize(row["ts"]).astimezone(LOCAL), TEMPLATE3))
