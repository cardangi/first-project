# -*- coding: utf-8 -*-
import os
import json
import argparse
from operator import itemgetter
from Applications import shared
from Applications.Database.RippedCD.shared import select

__author__ = 'Xavier ROSSET'


# ==========
# Constants.
# ==========
OUTPUT, KEYS = os.path.join(os.path.expandvars("%TEMP%"), "rippedcd.json"), ["RIPPED", "ARTISTSORT", "ALBUMSORT", "ARTIST", "YEAR", "ALBUM", "GENRE", "BARCODE", "APPLICATION"]


# ==========
# Functions.
# ==========
def validdb(arg):
    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(arg))
    return arg


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ================
# Initializations.
# ================
args, arguments = [], parser.parse_args()


# ===============
# Main algorithm.
# ===============
for item in sorted(select(arguments.database), key=itemgetter(0), reverse=True):
    args.append((itemgetter(0)(item), dict(zip(KEYS, [shared.dateformat(shared.LOCAL.localize(itemgetter(1)(item)), shared.TEMPLATE4),
                                                      itemgetter(9)(item),
                                                      itemgetter(8)(item),
                                                      itemgetter(2)(item),
                                                      itemgetter(3)(item),
                                                      itemgetter(4)(item),
                                                      itemgetter(6)(item),
                                                      itemgetter(5)(item),
                                                      itemgetter(7)(item)
                                                      ]))))
args = [shared.now(), dict(args)]
print(args)
if args:
    with open(OUTPUT, mode=shared.WRITE, encoding=shared.UTF8) as fp:
        json.dump(args, fp, indent=4, sort_keys=True)