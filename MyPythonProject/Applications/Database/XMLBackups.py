# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import xml.etree.ElementTree as ET
from pytz import timezone
import sqlite3
import os


# =================
# Relative imports.
# =================
from .. import shared


# ===============
# Main algorithm.
# ===============

# 1. Parse XML tree.
tree = ET.parse(os.path.join(os.path.expandvars("%temp%"), "output1.xml"))
root = tree.getroot()

# 2. Connexion à la base de données.
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row

# 3. Append last backup date.
for target in root.findall("./workspace/target"):
    for data in conn.cursor().execute("SELECT lastbackup FROM backup WHERE id=?", (target.attrib["uid"],)):
        lastbackup = ET.SubElement(target, "lastbackupdate")
        lastbackup.text = shared.dateformat(timezone(shared.DFTTIMEZONE).localize(data["lastbackup"]), shared.TEMPLATE1)

# 4. Déconnexion de la base de données.
conn.close()

# 5. Output XML modified tree.
tree.write(os.path.join(os.path.expandvars("%temp%"), "output2.xml"))
