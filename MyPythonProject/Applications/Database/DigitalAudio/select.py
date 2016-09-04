# -*- coding: ISO-8859-1 -*-
from collections import OrderedDict
from pprint import PrettyPrinter
from operator import itemgetter
import argparse
import sqlite3
import locale
import json
import sys
import os
from ... import shared as s1
from ..Modules import shared as s2

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


# ==============
# SQL converter.
# ==============
sqlite3.register_converter("boolean", s2.convert_boolean)


# ================
# Initializations.
# ================
status, parent, arguments = 100, None, parser.parse_args()


# ===============
# Main algorithm.
# ===============


#     -----------------------
#  1. Extraction des données.
#     -----------------------
with s2.connectto(s1.DATABASE) as c:

    if c.execute("SELECT count(*) FROM {0} WHERE rowid=?".format(arguments.table), (arguments.uid,)).fetchone()[0]:

        for row in c.execute("SELECT {statement}, created FROM {table} WHERE rowid=?".format(statement=", ".join(FIELDS[arguments.table]), table=arguments.table), (arguments.uid,)):
            templist1 = [(field, row[field]) for field in FIELDS[arguments.table]]
            templist1.append(("created", s1.dateformat(s1.LOCAL.localize(row["created"]), s1.TEMPLATE4)))
            parent = OrderedDict(sorted(templist1, key=itemgetter(0)))
    
            if arguments.table in ["albums", "discs"]:
    
                if arguments.table == "albums":
                    for subrow in c.execute("SELECT {statement}, created FROM discs WHERE albumid=?".format(statement=", ".join(FIELDS["discs"])), (row["albumid"],)):
                        templist2 = [(field, subrow[field]) for field in FIELDS["discs"]]
                        templist2.append(("created", s1.dateformat(s1.LOCAL.localize(subrow["created"]), s1.TEMPLATE4)))
                        disc = OrderedDict(sorted(templist2, key=itemgetter(0)))
    
                        for ssubrow in c.execute("SELECT {statement}, created FROM tracks WHERE albumid=? and discid=?".format(statement=", ".join(FIELDS["tracks"])), (row["albumid"], subrow["discid"])):
                            templist3 = [(field, ssubrow[field]) for field in FIELDS["tracks"]]
                            templist3.append(("created", s1.dateformat(s1.LOCAL.localize(ssubrow["created"]), s1.TEMPLATE4)))
                            disc["track_{0}".format(str(ssubrow["trackid"]).zfill(2))] = OrderedDict(sorted(templist3, key=itemgetter(0)))
                        parent["disc_{0}".format(str(subrow["discid"]).zfill(2))] = disc
    
                elif arguments.table == "discs":
                    for subrow in c.execute("SELECT {statement}, created FROM tracks WHERE albumid=? and discid=?".format(statement=", ".join(FIELDS["tracks"])), (row["albumid"], row["discid"])):
                        templist3 = [(field, subrow[field]) for field in FIELDS["tracks"]]
                        templist3.append(("created", s1.dateformat(s1.LOCAL.localize(subrow["created"]), s1.TEMPLATE4)))
                        parent["track_{0}".format(str(subrow["trackid"]).zfill(2))] = OrderedDict(sorted(templist3, key=itemgetter(0)))


#     ------------------------
#  2. Restitution des données.
#     ------------------------
if parent:
    status = 0

    #  2.a. Edition écran.
    if arguments.print:
        pp = PrettyPrinter(indent=4, width=160)
        pp.pprint(parent)

    #  2.b. Edition fichier.
    with open(OUTFILE, mode=s1.WRITE) as fp:
        json.dump([s1.now(), arguments.table.upper(), arguments.uid, parent], fp, indent=4)


#     ---------------------------------------------------
#  3. Communication du code retour au programme appelant.
#     ---------------------------------------------------
sys.exit(status)
