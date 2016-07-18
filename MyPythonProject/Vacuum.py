# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'

import sqlite3

conn = sqlite3.connect(r"g:\computing\database.db")
conn.execute("VACUUM")
conn.close()
