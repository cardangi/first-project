# -*- coding: utf-8 -*-
from jinja2 import Environment, FileSystemLoader
from logging.config import dictConfig
import argparse
import logging
import sqlite3
import locale
import yaml
import os

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment1.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml")) as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("info.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))


# ==========
# Constants.
# ==========
ALBUMS = ["id", "albumid", "artist", "year", "album", "discs", "genre", "upc"]
DISCS = ["id", "albumid", "discid"]
TRACKS = ["id", "albumid", "discid", "trackid", "title"]


# ======================
# Jinja2 environment1(s).
# ======================
environment1 = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Database", "DigitalAudio", "Templates")), trim_blocks=True, lstrip_blocks=True)
environment2 = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Database", "Templates")), trim_blocks=True, lstrip_blocks=True)


# ===================
# Jinja2 template(s).
# ===================
content = environment1.get_template("Content")
t3 = environment2.get_template("T3")
t4 = environment2.get_template("T4")
t5 = environment2.get_template("T5")


# ==========
# Functions.
# ==========
def validdb(arg):
    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(arg))
    return arg


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ================
# Initializations.
# ================
albums, discs, tracks, arguments = [], [], [], parser.parse_args()


# ===============
# Main algorithm.
# ===============
c = sqlite3.connect(arguments.database, detect_types=sqlite3.PARSE_DECLTYPES)
c.row_factory = sqlite3.Row
for album in c.execute("SELECT rowid, albumid, artist, year, album, discs, genre, upc FROM albums ORDER BY rowid"):
    albums.append(album)
    for disc in c.execute("SELECT rowid, albumid, discid FROM discs WHERE albumid=? ORDER BY rowid", (album["albumid"],)):
        discs.append(disc)
        for track in c.execute("SELECT rowid, albumid, discid, trackid, title FROM tracks WHERE albumid=? and discid=? ORDER BY rowid", (album["albumid"], disc["discid"])):
            tracks.append(track)
print(content.render(content="{0}{1}{2}".format(t3.render(id="albums", h2="albums", th=ALBUMS, tr=albums),
                                                t4.render(id="discs", h2="discs", th=DISCS, tr=discs),
                                                t5.render(id="tracks", h2="tracks", th=TRACKS, tr=tracks)
                                                )
                     )
      )
c.close()
