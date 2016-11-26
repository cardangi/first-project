# -*- coding: utf-8 -*-
from jinja2 import Environment, FileSystemLoader
from Applications.shared import WRITE, UTF8
from logging.config import dictConfig
import argparse
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
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))


# ==========
# Constants.
# ==========
ALBUMS = ["id", "albumid", "artist", "year", "album", "discs", "genre", "upc"]
DISCS = ["id", "albumid", "discid"]
TRACKS = ["id", "albumid", "discid", "trackid", "title"]
HTML = os.path.join(os.path.expandvars("%_COMPUTING%"), "digitalaudiobase", "rawview.html")


# =====================
# Jinja2 environment(s).
# =====================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "DigitalAudioFiles")), trim_blocks=True, lstrip_blocks=True)


# ===================
# Jinja2 template(s).
# ===================
content = environment.get_template("Content")
t3 = environment.get_template("T3")
t4 = environment.get_template("T4")
t5 = environment.get_template("T5")


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
if albums:
    with open(HTML, mode=WRITE, encoding=UTF8) as fw:
        fw.write(content.render(content="{0}{1}{2}".format(t3.render(id="albums", h2="albums", th=ALBUMS, tr=albums),
                                                           t4.render(id="discs", h2="discs", th=DISCS, tr=discs),
                                                           t5.render(id="tracks", h2="tracks", th=TRACKS, tr=tracks)
                                                           )
                                )
                 )
c.close()
