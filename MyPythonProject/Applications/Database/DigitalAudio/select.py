# -*- coding: ISO-8859-1 -*-
from collections import OrderedDict
from pprint import PrettyPrinter
import argparse
import sqlite3
import locale
import json
import sys
import os
from ... import shared

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--print", action="store_true")
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
OUTFILE = os.path.join(os.path.expandvars("%TEMP%"), "content.json")
FIELDS = {"albums": ["rowid", "albumid", "artist", "year", "album", "genre", "upc", "discs", "live", "bootleg", "incollection", "encodingyear", "origyear", "language"],
          "discs": ["rowid", "albumid", "discid", "tracks"],
          "tracks": ["rowid", "albumid", "discid", "trackid", "title"]}


# ==========
# Functions.
# ==========
def convert_boolean(f):
    if int(f):
        return True
    return False
sqlite3.register_converter("boolean", convert_boolean)


# ================
# Initializations.
# ================
status, parent, arguments = 100, None, parser.parse_args()


# ===============
# Main algorithm.
# ===============


#  1. Ouverture de la connexion à la base de données.
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row


#  2. Extraction des données.
if conn.cursor().execute("SELECT count(*) FROM {0} WHERE rowid=?".format(arguments.table), (arguments.uid,)).fetchone()[0]:
    for row in conn.cursor().execute("SELECT {statement}, created FROM {table} WHERE rowid=?".format(statement=", ".join(FIELDS[arguments.table]), table=arguments.table), (arguments.uid,)):
        templist1 = [(field, row[field]) for field in FIELDS[arguments.table]]
        templist1.append(("created", shared.dateformat(shared.LOCAL.localize(row["created"]), shared.TEMPLATE4)))
        parent = OrderedDict(sorted(templist1, key=lambda i: i[0]))

        if arguments.table in ["albums", "discs"]:

            if arguments.table == "albums":
                for subrow in conn.cursor().execute("SELECT {statement}, created FROM discs WHERE albumid=?".format(statement=", ".join(FIELDS["discs"])), (row["albumid"],)):
                    templist2 = [(field, subrow[field]) for field in FIELDS["discs"]]
                    templist2.append(("created", shared.dateformat(shared.LOCAL.localize(subrow["created"]), shared.TEMPLATE4)))
                    disc = OrderedDict(sorted(templist2, key=lambda i: i[0]))

                    for ssubrow in conn.cursor().execute("SELECT {statement}, created FROM tracks WHERE albumid=? and discid=?".format(statement=", ".join(FIELDS["tracks"])), (row["albumid"], subrow["discid"])):
                        templist3 = [(field, ssubrow[field]) for field in FIELDS["tracks"]]
                        templist3.append(("created", shared.dateformat(shared.LOCAL.localize(ssubrow["created"]), shared.TEMPLATE4)))
                        disc["track_{0}".format(str(ssubrow["trackid"]).zfill(2))] = OrderedDict(sorted(templist3, key=lambda i: i[0]))
                    parent["disc_{0}".format(str(subrow["discid"]).zfill(2))] = disc

            elif arguments.table == "discs":
                for subrow in conn.cursor().execute("SELECT {statement}, created FROM tracks WHERE albumid=? and discid=?".format(statement=", ".join(FIELDS["tracks"])), (row["albumid"], row["discid"])):
                    templist3 = [(field, subrow[field]) for field in FIELDS["tracks"]]
                    templist3.append(("created", shared.dateformat(shared.LOCAL.localize(subrow["created"]), shared.TEMPLATE4)))
                    parent["track_{0}".format(str(subrow["trackid"]).zfill(2))] = OrderedDict(sorted(templist3, key=lambda i: i[0]))


#  3. Restitution des données.
if parent:
    status = 0

    #  3.a. Edition écran.
    if arguments.print:
        pp = PrettyPrinter(indent=4, width=160)
        pp.pprint(parent)

    #  3.b. Edition fichier.
    with open(OUTFILE, mode=shared.WRITE) as fp:
        json.dump([shared.now(), arguments.table.upper(), arguments.uid, parent], fp, indent=4)


#  4. Fermeture de la connexion à la base de données.
conn.close()


#  5. Communication du code retour au programme appelant.
sys.exit(status)
