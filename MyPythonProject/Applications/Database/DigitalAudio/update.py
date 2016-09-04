# -*- coding: ISO-8859-1 -*-
import argparse
import locale
from ... import shared as s1
from ..Modules import shared as s2

__author__ = 'Xavier ROSSET'


# =======================
# How to use this script?
# =======================
#  1. update.py albums 1 2 3 --artist "newartist" --album "newalbum"
#  2. update.py discs 1 2 3 --field "newvalue"
#  3. update.py tracks 1 2 3 --title "newtitle"


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
parser_updatalb = subparsers.add_parser("albums")
parser_updatalb.add_argument("uid", type=int, nargs="+")
parser_updatalb.add_argument("--artist", help="Artist")
parser_updatalb.add_argument("--year", help="Year", type=int)
parser_updatalb.add_argument("--album", help="Album title")
parser_updatalb.add_argument("--genre", help="Genre")
parser_updatalb.add_argument("--discs", help="Discs number", type=int)

# ----- Table "TRACKS".
parser_updattck = subparsers.add_parser("tracks")
parser_updattck.add_argument("uid", type=int, nargs="+")
parser_updattck.add_argument("--title", help="Title")

# ----- Table "DISCS".
parser_updatdsc = subparsers.add_parser("discs")
parser_updatdsc.add_argument("uid", type=int, nargs="+")
parser_updatdsc.add_argument("--field", help="Define here the field to update")


# ================
# Initializations.
# ================
update, where, args, arguments = "", "", (), parser.parse_args()


# ===============
# Main algorithm.
# ===============
with s2.connectto(s1.DATABASE) as c:

    #     -------------
    #  1. Clause "set".
    #     -------------
    if arguments.table == "albums":
        if arguments.artist:
            update = "{0}artist=?, ".format(update)
            args += (arguments.artist,)
        if arguments.year:
            update = "{0}year=?, ".format(update)
            args += (arguments.year,)
        if arguments.album:
            update = "{0}album=?, ".format(update)
            args += (arguments.album,)
        if arguments.genre:
            update = "{0}genre=?, ".format(update)
            args += (arguments.genre,)

    elif arguments.table == "discs":
        if arguments.field:
            update = "{0}field=?, ".format(update)
            args += (arguments.toto,)

    elif arguments.table == "tracks":
        if arguments.title:
            update = "{0}title=?, ".format(update)
            args += (arguments.title,)

    #     ---------------
    #  2. Clause "where".
    #     ---------------
    for id in arguments.uid:
        where = "{0}?, ".format(where)
        args += (id,)

    #     ------------------------
    #  3. Exécution de la requête.
    #     ------------------------
    if update:
        c.execute("UPDATE {0} SET {1} WHERE rowid IN ({2})".format(arguments.table, update[:-2], where[:-2]), args)
