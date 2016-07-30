# -*- coding: ISO-8859-1 -*-
import sys
import locale
import sqlite3
import argparse
from pytz import timezone
from datetime import datetime
from ... import shared

__author__ = 'Xavier ROSSET'


# =======================
# How to use this script?
# =======================
#  1. dbBackup.py select 123456797
#  2. dbBackup.py delete --uid 123456797 123456798
#  3. dbBackup.py delete
#  4. dbBackup.py update 123456797 123456798
#  5. dbBackup.py update 123456797 123456798 -t 1461004077


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command")
# -----
parser_del = subparsers.add_parser("delete")
parser_del.add_argument("--uid", help="Facultative backup script unique ID", nargs="*", type=int)
# -----
parser_sel = subparsers.add_parser("select")
parser_sel.add_argument("uid", help="Mandatory backup script unique ID", type=int)
# -----
parser_upd = subparsers.add_parser("update")
parser_upd.add_argument("uid", help="Mandatory backup script unique ID", nargs="+", type=int)
parser_upd.add_argument("-t", "--timestamp", help="Last backup date timestamp", type=int, nargs="?", default=int(datetime.now().timestamp()))


# ================
# Initializations.
# ================
status, arguments = 99, parser.parse_args()


# ===============
# Main algorithm.
# ===============

#  1. Connexion à la base de données.
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)

#  2. Suppression d'un script.
if arguments.command == "delete":
    status = 0
    if arguments.uid:
        for key in arguments.uid:
            conn.cursor().execute("DELETE FROM backup WHERE id=?", (key,))
    if not arguments.uid:
        conn.cursor().execute("DELETE FROM backup")

#  3. Sélection d'un script.
elif arguments.command == "select":
    if conn.cursor().execute("SELECT count(*) FROM backup WHERE id=?", (arguments.uid,)).fetchone()[0]:
        status = 0
        print(shared.dateformat(timezone(shared.DFTTIMEZONE).localize(conn.cursor().execute("SELECT lastbackup FROM backup WHERE id=?", (arguments.uid,)).fetchone()[0]), shared.TEMPLATE1))

#  4. Mise à jour de la date de dernière exécution du script.
#     Le script est créé si il n'existe pas.
elif arguments.command == "update":
    status = 0
    for key in arguments.uid:
        if conn.cursor().execute("SELECT count(*) FROM backup WHERE id=?", (key,)).fetchone()[0]:
            conn.cursor().execute("UPDATE backup SET lastbackup=? WHERE id=?", (datetime.fromtimestamp(arguments.timestamp), key))
        else:
            conn.cursor().execute("INSERT INTO backup (id, lastbackup) VALUES(?, ?)", (key, datetime.fromtimestamp(arguments.timestamp)))

#  5. Mise à jour de la base de données.
conn.commit()

#  6. Déconnexion de la base de données.
conn.close()

#  7. Communication du code retour au programme appelant.
sys.exit(status)
