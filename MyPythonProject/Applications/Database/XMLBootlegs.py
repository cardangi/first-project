# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import xml.etree.ElementTree as ET
from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
import os


# =================
# Relative imports.
# =================
from .. import shared


# ===============
# Main algorithm.
# ===============

# 1. Parse XML tree.
tree = ET.parse(os.path.join(os.path.expandvars("%temp%"), "bootlegs.xml"))
root = tree.getroot()

# 2. Append attribute to root tag.
root.set("update", shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE2))

# 3. Format bootleg date.
for date in root.findall("./Series/AlbumSort/Date"):
    date.text = "%s %s" % (parse(date.text).strftime("%B").capitalize(), parse(date.text).strftime("%d, %Y"))

# 4. Output XML modified tree.
tree.write(os.path.join(os.path.expandvars("%temp%"), "output.xml"))
