# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# ===================
# Absolute import(s).
# ===================
import sys
import sqlite3
import argparse
from datetime import datetime


# ===================
# Relative import(s).
# ===================
from .. import shared


# ==========
# Functions.
# ==========
def validyear(s):
    import re
    regex = re.compile(r"^(19[6-9]|20[0-2])\d$")
    if not regex.match(s):
        raise argparse.ArgumentTypeError('"{0}" is not a valid year'.format(s))
    return int(s)


def validalbumsort(s):
    import re
    regex = re.compile("^(?=[\d\.]+$)(?=.\.[^\.]+\..$)(?=\d\.\d{8}\.\d$).\.(?:19[6-9]|20[01])\d{5}\..$")
    if not regex.match(s):
        raise argparse.ArgumentTypeError('"{0}" is not a valid albumsort'.format(s))
    return s


def validbarcode(s):
    import re
    regex = re.compile("^\d{12,13}$")
    if s:
        if not regex.match(s):
            raise argparse.ArgumentTypeError('"{0}" is not a valid barcode'.format(s))
    return s


def validepoch(s):
    import re
    regex = re.compile("^\d{10}$")
    if not regex.match(s):
        raise argparse.ArgumentTypeError('"{0}" is not a valid epoch'.format(s))
    return int(s)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")

# INSERT command.
parser_ins = subparsers.add_parser("insert")
parser_ins.add_argument("artist")
parser_ins.add_argument("year", type=validyear)
parser_ins.add_argument("album")
parser_ins.add_argument("genre", choices=["Rock", "Hard Rock", "Heavy Metal", "Trash Metal", "Alternative Rock", "Black Metal", "Progressive Rock"])
parser_ins.add_argument("barcode", type=validbarcode)
parser_ins.add_argument("albumsort", type=validalbumsort)
parser_ins.add_argument("artistsort")

# UPDATE command.
parser_upd = subparsers.add_parser("update")
parser_upd.add_argument("uid", nargs="+", help="Mandatory record unique ID", type=int)
parser_upd.add_argument("--ripped", type=validepoch)
parser_upd.add_argument("--artistsort")
parser_upd.add_argument("--albumsort", type=validalbumsort)
parser_upd.add_argument("--artist")
parser_upd.add_argument("--year", type=validyear)
parser_upd.add_argument("--album")
parser_upd.add_argument("--genre", choices=["Rock", "Hard Rock", "Heavy Metal", "Trash Metal", "Alternative Rock", "Black Metal", "Progressive Rock"])
parser_upd.add_argument("--barcode", type=validbarcode)

# DELETE command.
parser_del = subparsers.add_parser("delete")
parser_del.add_argument("uid", nargs="+", help="Mandatory record unique ID", type=int)


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ===============
# Main algorithm.
# ===============

#  1. Ouverture de la connexion à la base de données.
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)

#  2. Insertion d'un CD.
if arguments.command == "insert":
    conn.cursor().execute("INSERT INTO rippinglog (ripped, artist, year, album, UPC, genre, application, albumsort, artistsort) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (datetime.now(),
                                                                                                                                                                     arguments.artist,
                                                                                                                                                                     arguments.year,
                                                                                                                                                                     arguments.album,
                                                                                                                                                                     arguments.barcode,
                                                                                                                                                                     arguments.genre,
                                                                                                                                                                     "dBpoweramp 15.1",
                                                                                                                                                                     arguments.albumsort,
                                                                                                                                                                     arguments.artistsort
                                                                                                                                                                     )
                          )

#  3. Mise à jour d'un CD.
elif arguments.command == "update":
    for uid in arguments.uid:
        statment, args = "", ()
        if conn.cursor().execute("SELECT count(*) FROM rippinglog WHERE id=?", (uid,)).fetchone()[0]:
            if arguments.ripped:
                statment = '{0}ripped=?, '.format(statment)
                args += (datetime.fromtimestamp(arguments.ripped),)
            if arguments.artistsort:
                statment = '{0}artistsort=?, '.format(statment)
                args += (arguments.artistsort,)
            if arguments.albumsort:
                statment = '{0}albumsort=?, '.format(statment)
                args += (arguments.albumsort,)
            if arguments.artist:
                statment = '{0}artist=?, '.format(statment)
                args += (arguments.artist,)
            if arguments.year:
                statment = '{0}year=?, '.format(statment)
                args += (arguments.year,)
            if arguments.album:
                statment = '{0}album=?, '.format(statment)
                args += (arguments.album,)
            if arguments.genre:
                statment = '{0}genre=?, '.format(statment)
                args += (arguments.genre,)
            if arguments.barcode:
                statment = '{0}UPC=?, '.format(statment)
                args += (arguments.barcode,)
            if statment:
                args += (uid,)
                conn.cursor().execute("UPDATE rippinglog SET {0} WHERE id=?".format(statment[:-2]), args)

#  4. Suppression d'un CD.
elif arguments.command == "delete":
    for uid in arguments.uid:
        if conn.cursor().execute("SELECT count(*) FROM rippinglog WHERE id=?", (uid,)).fetchone()[0]:
            conn.cursor().execute("DELETE FROM rippinglog WHERE id=?", (uid,))

#  5. Mise à jour de la base de données.
conn.commit()

#  6. Fermeture de la connexion à la base de données.
conn.close()

#  7. Communication du code retour au programme appelant.
sys.exit(0)
