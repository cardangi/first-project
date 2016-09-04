# -*- coding: ISO-8859-1 -*-
import argparse
import sqlite3
import locale
from ... import shared as s1
from ..Modules import shared as s2

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


# ==============
# SQL converter.
# ==============
sqlite3.register_converter("boolean", s2.convert_boolean)


# ===============
# Main algorithm.
# ===============
with s2.connectto(s1.DATABASE) as c:

    #  1. Clause "where".
    for id in arguments.uid:
        where = "{0}?, ".format(where)
        args += (id,)
    
    #  2. Extraction des valeurs "ALBUMID" et "DISCID" pour permettre la suppression des enregistrements
    #     des tables "DISCS" et "TRACKS".
    for row1 in c.execute("SELECT albumid FROM albums WHERE rowid IN ({0}) ORDER BY albumid".format(where[:-2]), args):
        for row2 in c.execute("SELECT discid FROM discs WHERE albumid=?", (row1["albumid"],)):
            discs.append((row1["albumid"], row2["discid"]))
    
    #  3. Exécution de la requête.
    c.execute("DELETE FROM albums WHERE rowid IN ({0})".format(where[:-2]), args)
    
    #  4. Suppression des enregistrements dépendants.
    for i, j in discs:
        c.execute("DELETE FROM discs WHERE albumid=? and discid=?", (i, j))
        c.execute("DELETE FROM tracks WHERE albumid=? and discid=?", (i, j))
