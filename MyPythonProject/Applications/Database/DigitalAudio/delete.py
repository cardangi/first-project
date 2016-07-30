# -*- coding: ISO-8859-1 -*-
import argparse
import sqlite3
import locale
from ... import shared

__author__ = 'Xavier ROSSET'


# =======================
# How to use this script?
# =======================
# 1. delete.py 100
# 2. delete.py 100 101 102 103


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("uid", type=int, nargs="+")


# ================
# Initializations.
# ================
where, discs, args, arguments = "", [], (), parser.parse_args()


# ===============
# Main algorithm.
# ===============

#  1. Ouverture de la connexion à la base de données.
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row

#  2. Construction de la clause "where".
for id in arguments.uid:
    where = "{0}?, ".format(where)
    args += (id,)

#  3. Extraction des valeurs "ALBUMID" et "DISCID" pour permettre la suppression des enregistrements
#     des tables "DISCS" et "TRACKS".
for row1 in conn.cursor().execute("SELECT albumid FROM albums WHERE rowid IN ({0}) ORDER BY albumid".format(where[:-2]), args):
    for row2 in conn.cursor().execute("SELECT discid FROM discs WHERE albumid=?", (row1["albumid"],)):
        discs.append((row1["albumid"], row2["discid"]))

#  4. Exécution de la requête.
conn.cursor().execute("DELETE FROM albums WHERE rowid IN ({0})".format(where[:-2]), args)

#  5. Suppression des enregistrements dépendants.
for i, j in discs:
    conn.cursor().execute("DELETE FROM discs WHERE albumid=? and discid=?", (i, j))
    conn.cursor().execute("DELETE FROM tracks WHERE albumid=? and discid=?", (i, j))

#  6. Mise à jour de la base de données.
conn.commit()

#  7. Fermeture de la connexion à la base de données.
conn.close()
