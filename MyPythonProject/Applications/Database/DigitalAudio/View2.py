# -*- coding: utf-8 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from itertools import repeat
from pytz import timezone
import sqlite3
import logging
import locale
import os


# =================
# Relative imports.
# =================
from ... import shared


# ==========================
# Define French environment1.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ==========
# Constants.
# ==========
ALBUMS = ["id", "albumid", "artist", "year", "album", "discs", "genre", "upc"]
DISCS = ["id", "albumid", "discid"]
TRACKS = ["id", "albumid", "discid", "trackid", "title"]


# ================
# Initializations.
# ================
albums, discs, tracks = [], [], []


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


# ===============
# Main algorithm.
# ===============


#    ---------------
#  1. Start logging.
#    ---------------
logger.info("{0} {1} {0}".format("".join(list(repeat("=", 50))), shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1)))
logger.info('START "%s".' % (os.path.basename(__file__),))


#    -----------------------------------------------
#  2. Ouverture de la connexion à la base de données.
#    -----------------------------------------------
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row


#    -----------------------
#  3. Extraction des données.
#    -----------------------
for album in conn.cursor().execute("SELECT rowid, albumid, artist, year, album, discs, genre, upc FROM albums ORDER BY rowid"):
    albums.append(album)
    for disc in conn.cursor().execute("SELECT rowid, albumid, discid FROM discs WHERE albumid=? ORDER BY rowid", (album["albumid"],)):
        discs.append(disc)
        for track in conn.cursor().execute("SELECT rowid, albumid, discid, trackid, title FROM tracks WHERE albumid=? and discid=? ORDER BY rowid", (album["albumid"], disc["discid"])):
            tracks.append(track)


#    -----------------------------------------------
#  4. Fermeture de la connexion à la base de données.
#    -----------------------------------------------
conn.close()


#    ------------------------
#  5. Restitution des données.
#    ------------------------
print(content.render(content="{0}{1}{2}".format(t3.render(id="albums", h2="albums", th=ALBUMS, tr=albums),
                                                t4.render(id="discs", h2="discs", th=DISCS, tr=discs),
                                                t5.render(id="tracks", h2="tracks", th=TRACKS, tr=tracks)
                                                )
                     )
      )


#    --------------
#  6. Stop logging.
#    --------------
logger.info('END "%s".' % (os.path.basename(__file__),))
