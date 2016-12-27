# -*- coding: utf-8 -*-
import sqlite3
import logging
import datetime
from itertools import repeat
from Applications.shared import DATABASE

__author__ = 'Xavier ROSSET'


# =========
# Mappings.
# =========
MAPPING = {"rundates": "rundate", "backups": "backup"}


# ===================================
# Main functions to work with tables.
# ===================================
def select(table, db=DATABASE):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    for row in conn.execute("SELECT * FROM {0} ORDER BY id".format(table)):
        logger = logging.getLogger("{0}.select".format(__name__))
        logger.debug("Table          : {0}".format(table))
        logger.debug("Selected record:")
        for item in tuple(row):
            logger.debug("\t{0}".format(item).expandtabs(3))
        yield tuple(row)


def selectfromuid(uid, table, db=DATABASE):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    for row in conn.execute("SELECT * FROM {0} WHERE rowid=?".format(table), (uid,)):
        logger = logging.getLogger("{0}.selectfromuid_rundates".format(__name__))
        logger.debug("Table          : {0}".format(table))
        logger.debug("Selected record:")
        logger.debug("Unique ID: {0:>4d}.".format(uid))
        for item in tuple(row):
            logger.debug("\t{0}".format(item).expandtabs(3))
        yield tuple(row)


def insert(*uid, db=DATABASE, table=None, date=None):
    if table is None:
        return 0
    if table not in MAPPING:
        return 0
    if date is None:
        date = datetime.datetime.utcnow()
    conn = sqlite3.connect(db)
    with conn:
        conn.executemany("INSERT INTO {0} (id, {1}) VALUES(?, ?)".format(table, MAPPING[table]), zip(uid, repeat(date)))
        status = conn.total_changes
        logger = logging.getLogger("{0}.insert_rundates".format(__name__))
        logger.debug("Table: {0}".format(table))
        logger.debug("{0} records inserted.".format(status))
    return status
