# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =======================
# How to use this script?
# =======================
# select.py albums 100 > "%_result%"
# IF NOT ERRORLEVEL 1 (
#     FOR /F "usebackq delims=; tokens=1-6" %%i IN ("%_result%") DO (
#         ECHO albumid: %%i
#         ECHO artist: %%j
#         ECHO year: %%k
#         ECHO album: %%l
#         ECHO genre: %%m
#         ECHO upc: %%n
#     )
# )
# IF ERRORLEVEL 1 ECHO Record number 100 doesn't exist in Albums table.


# =================
# Absolute imports.
# =================
import argparse
import sqlite3
import locale
import sys


# =================
# Relative imports.
# =================
from ... import shared


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="table")

# ----- Table "ALBUMS".
parser_selectalb = subparsers.add_parser("albums")
parser_selectalb.add_argument("uid", type=int)

# ----- Table "DISCS".
parser_selectdsc = subparsers.add_parser("discs")
parser_selectdsc.add_argument("uid", type=int)

# ----- Table "TRACKS".
parser_selecttck = subparsers.add_parser("tracks")
parser_selecttck.add_argument("uid", type=int)


# ==========
# Constants.
# ==========
qry = {"albums": "SELECT albumid, artist, year, album, genre, upc FROM albums WHERE rowid=?", "discs": "SELECT albumid, discid, FROM discs WHERE rowid=?", "tracks": "SELECT albumid, discid, trackid, title FROM tracks WHERE rowid=?"}


# ================
# Initializations.
# ================
status, o, iterable, arguments = 100, "", None, parser.parse_args()


# ===============
# Main algorithm.
# ===============

#  1. Ouverture de la connexion à la base de données.
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row

#  2. Contrôle de l'existence de l'enregistrement.
count = conn.cursor().execute("SELECT count(*) FROM {0} WHERE rowid=?".format(arguments.table), (arguments.uid,)).fetchone()[0]
if count > 0:
    iterable = conn.cursor().execute(qry[arguments.table], (arguments.uid,)).fetchone()
    for i in range(0, len(iterable)):
        o = "{0}{1};".format(o, iterable[i])
    if o:
        print(o[:-1])
        status = 0

#  3. Fermeture de la connexion à la base de données.
conn.close()

#  4. Communication du code retour au programme appelant.
sys.exit(status)
