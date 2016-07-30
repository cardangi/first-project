# -*- coding: ISO-8859-1 -*-
from pprint import PrettyPrinter
import argparse
import sqlite3
import json
import os
from .. import shared

__author__ = 'Xavier ROSSET'


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--table", default="sqlite_master")
parser.add_argument("-p", "--print", action="store_true")


# ==========
# Constants.
# ==========
OUTFILE = os.path.join(os.path.expandvars("%TEMP%"), "sqlite_master.json")


# ================
# Initializations.
# ================
pp, arguments = PrettyPrinter(indent=4, width=160), parser.parse_args()


# ===============
# Main algorithm.
# ===============

#  1. Ouverture de la connexion à la base de données.
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)

#  2. Restitution des tables.
r = [row for row in conn.cursor().execute("SELECT * FROM {table} ORDER BY rowid".format(table=arguments.table))]
if arguments.print:
    pp.pprint(r)
with open(OUTFILE, mode=shared.WRITE) as fp:
    json.dump(r, fp, indent=4)

#  3. Fermeture de la connexion à la base de données.
conn.close()
