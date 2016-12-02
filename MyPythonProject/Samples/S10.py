# -*- coding: uft-8 -*-
from datetime import datetime
from itertools import repeat
from pytz import timezone
import json
from . import shared

__author__ = 'Xavier ROSSET'


# ==========
# Constants.
# ==========
ZONES = ["US/Pacific", "US/Eastern", "Indian/Mayotte", "Asia/Tokyo", "Australia/Sydney"]


# ==========
# Functions.
# ==========
def titi(ep, iterable, pos=0):
    return iterable.insert(pos, ep)

def tutu(ep, iterable, pos=0):
     return iterable.insert(pos, shared.dateformat(timezone("UTC").localize(datetime.utcfromtimestamp(ep)), shared.TEMPLATE3))

def toto(start, end, zone=shared.DFTTIMEZONE):

    if start > end:
        raise ValueError()
    epochlist, epoch, zones = [], list(range(start, end + 1)), list(ZONES)
    zones.insert(2, arguments.zone)
    epochlist = [list(i) for i in zip(*[list(map(shared.getdatetime, epoch, repeat(zone))) for zone in zones]))]  # [(1-US/Pacific, 1-US/Eastern, 1-Indian/Mayotte), (2-US/Pacific, 2-US/Eastern, 2-Indian/Mayotte), (3-US/Pacific, 3-US/Eastern, 3-Indian/Mayotte)]
    epochlist = list(map(titi, epoch, epochlist))
    return list(map(tutu, epoch, epochlist, repeat(1)))  # [(1, 1-UTC, 1-US/Pacific, 1-US/Eastern, 1-Indian/Mayotte), (2, 2-UTC, 2-US/Pacific, 2-US/Eastern, 2-Indian/Mayotte), (3, 3-UTC, 3-US/Pacific, 3-US/Eastern, 3-Indian/Mayotte)]


# Script 1.
try:
    x = toto(1480694200, 1480694203)
except ValueError:
    pass
else:
    if x:
        with open("toto.json", mode="w", encoding="utf-8"):
            json.dump(x, indent=4)


# Script 2.
try:
    x = toto(1480694200, 1480694203)
except ValueError:
    pass
else:
    if x:
        template.render(x)
