# -*- coding: utf-8 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from jinja2 import Environment, FileSystemLoader
from pytz import timezone
import sqlite3
import locale
import os


# =================
# Relative imports.
# =================
from ... import shared


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Database", "Templates")), trim_blocks=True, lstrip_blocks=True)


# ================
# Jinja2 template.
# ================
t2 = environment.get_template("T2")
content = environment.get_template("Content")


# ===============
# Main algorithm.
# ===============


#    -----------------------------------------------
# 1. Ouverture de la connexion à la base de données.
#    -----------------------------------------------
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row


#    -----------------------
# 2. Extraction des données.
#    -----------------------
tr = [(row["id"], shared.dateformat(timezone(shared.DFTTIMEZONE).localize(row["lastbackup"]), shared.TEMPLATE3)) for row in conn.cursor().execute("SELECT * FROM backup ORDER BY rowid")]


#    ------------------------
# 3. Restitution des données.
#    ------------------------
print(content.render(title="Last backup dates (raw view)", content=t2.render(id="backup", h1="Last Backup Dates", th=["id", "date"], tr=tr)))


#    -----------------------------------------------
# 4. Fermeture de la connexion à la base de données.
#    -----------------------------------------------
conn.close()
