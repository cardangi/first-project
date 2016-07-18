# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


import os
import operator
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
with open(os.path.join(os.path.expandvars("%temp%"), "audiotags.txt"), encoding=shared.UTF8) as fr:
    for row in fr:
        d.append((row.strip("\ufeff").splitlines()[0].split(";")[0], row.strip("\ufeff").splitlines()[0].split(";")[1]))

with open(os.path.join(os.path.expandvars("%temp%"), "audiotags.txt"), mode="w", encoding=shared.UTF8) as fw:
    for a, b in sorted(d, key=operator.itemgetter(0)):
        fw.write("{0};{1};dBpoweramp 15.1 on {2}\n".format(a, b, shared.dateformat(datetime.fromtimestamp(int(b), tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3)))
