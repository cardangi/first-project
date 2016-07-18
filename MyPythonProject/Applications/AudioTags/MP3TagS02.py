# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


import os
from pytz import timezone
from datetime import datetime
from Applications import shared


# ==========
# Variables.
# ==========
d = []


# ===============
# Main algorithm.
# ===============
with open(os.path.join(os.path.expandvars("%temp%"), "audiotags.txt"), mode="w", encoding=shared.UTF8) as fw:
    for i in range(34):
        fw.write("{0}\n".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3)))
