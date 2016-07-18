# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =======================
# How to use this script?
# =======================
#  1. dbLastRunDates.py select 123456797
#  2. dbLastRunDates.py delete --uid 123456797 123456798
#  3. dbLastRunDates.py delete
#  4. dbLastRunDates.py update 123456797 123456798
#  5. dbLastRunDates.py update 123456797 123456798 -t 1461004077


# =================
# Absolute imports.
# =================
from datetime import datetime, timedelta
from pytz import timezone
import sqlite3
import argparse
import locale
import sys


# =================
# Relative imports.
# =================
from .. import shared


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
parser_del.add_argument("--uid", help="Facultative task unique ID", type=int, nargs="*")
# -----
parser_sel = subparsers.add_parser("select")
parser_sel.add_argument("uid", help="Mandatory task unique ID", type=int)
# -----
parser_upd = subparsers.add_parser("update")
parser_upd.add_argument("uid", help="Mandatory task unique ID", type=int, nargs="+")
parser_upd.add_argument("-t", "--timestamp", help="Last run date timestamp", type=int, nargs="?", default=int(datetime.now().timestamp()))
# -----
parser_sum = subparsers.add_parser("delta")
parser_sum.add_argument("uid", help="Mandatory task unique ID", type=int)
parser_sum.add_argument("-t", "--timedelta", help="Time delta in days", type=int, nargs="?", default=0)


# ================
# Initializations.
# ================
status, arguments = 99, parser.parse_args()


# ===============
# Main algorithm.
# ===============

#  1. Ouverture de la connexion à la base de données.
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)

#  2. Sélection d'une tâche.
if arguments.command == "select":
    if conn.cursor().execute("SELECT count(*) FROM lastrundates WHERE id=?", (arguments.uid,)).fetchone()[0]:
        status = 0
        print(shared.dateformat(timezone(shared.DFTTIMEZONE).localize(conn.cursor().execute("SELECT lastrundate FROM lastrundates WHERE id=?", (arguments.uid,)).fetchone()[0]), shared.TEMPLATE1))

#  3. Suppression d'une tâche.
if arguments.command == "delete":
    status = 0
    if arguments.uid:
        for key in arguments.uid:
            conn.cursor().execute("DELETE FROM lastrundates WHERE id=?", (key,))
    if not arguments.uid:
        conn.cursor().execute("DELETE FROM lastrundates")

if arguments.command == "delta":
    status = 0
    if conn.cursor().execute("SELECT count(*) FROM lastrundates WHERE id=?", (arguments.uid,)).fetchone()[0]:
        now = datetime.now(tz=timezone(shared.DFTTIMEZONE))
        nextrundate = timezone(shared.DFTTIMEZONE).localize(conn.cursor().execute("SELECT lastrundate FROM lastrundates WHERE id=?", (arguments.uid,)).fetchone()[0]) + timedelta(days=arguments.timedelta)
        if now < nextrundate:
            status = 99
        # print(shared.dateformat(nextrundate, shared.TEMPLATE3))

#  5. Mise à jour de la date de dernière exécution d'une tâche.
#     La tâche est créée si elle n'existe pas.
elif arguments.command == "update":
    status = 0
    for key in arguments.uid:
        if conn.cursor().execute("SELECT count(*) FROM lastrundates WHERE id=?", (key,)).fetchone()[0]:
            conn.cursor().execute("UPDATE lastrundates SET lastrundate=? WHERE id=?", (datetime.fromtimestamp(arguments.timestamp), key))
        else:
            conn.cursor().execute("INSERT INTO lastrundates (id, lastrundate) VALUES(?, ?)", (key, datetime.fromtimestamp(arguments.timestamp)))

#  6. Mise à jour de la base de données.
conn.commit()

#  7. Fermeture de la connexion à la base de données.
conn.close()

#  8. Communication du code retour au programme appelant.
sys.exit(status)
