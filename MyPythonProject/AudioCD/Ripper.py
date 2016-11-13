# -*- coding: ISO-8859-1 -*-
import os
import json
# import logging
import argparse
from operator import itemgetter
from contextlib import ExitStack
from Applications.shared import WRITE
from Applications.AudioCD.shared import RippedCD, album


__author__ = 'Xavier ROSSET'


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("tagsfile", help="tags file")
parser.add_argument("rippingprofile", help="rip profile")
parser.add_argument("-t", "--test", action="store_true")


# ========
# Logging.
# ========
# logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ============
# Local names.
# ============
exists, join, expandvars = os.path.exists, os.path.join, os.path.expandvars


# ==========
# Constants.
# ==========
DABJSON, RIPDBJSON = join(expandvars("%TEMP%"), "digitalaudiodatabase.json"), join(expandvars("%TEMP%"), "rippinglog.json")


# ==========
# Variables.
# ==========
obj, arguments = [], parser.parse_args()


# ===============
# Main algorithm.
# ===============
stack = ExitStack()
try:
    rippedcd = stack.enter_context(RippedCD(arguments.rippingprofile, arguments.tagsfile, arguments.test))
except ValueError as e:
    pass
    # logger.debug(e)
    # logger.debug('END "%s".' % (os.path.basename(__file__),))
else:
    with stack:
        if rippedcd.profile in ["default", "selftitled"]:

            #  --> 1. Digital audio database.
            if exists(DABJSON):
                with open(DABJSON) as fp:
                    obj = json.load(fp)
                obj = [tuple(item) for item in obj]
            obj.append(
                tuple(
                    [
                        rippedcd.new.index,
                        rippedcd.new.albumsort[:-3],
                        rippedcd.new.titlesort,
                        rippedcd.new.artist,
                        rippedcd.new.year,
                        rippedcd.new.album,
                        rippedcd.new.genre,
                        rippedcd.new.discnumber,
                        rippedcd.new.totaldiscs,
                        rippedcd.new.label,
                        rippedcd.new.tracknumber,
                        rippedcd.new.totaltracks,
                        rippedcd.new.title,
                        rippedcd.new.live,
                        rippedcd.new.bootleg,
                        rippedcd.new.incollection,
                        rippedcd.new.upc,
                        rippedcd.new.encodingyear,
                        rippedcd.new.titlelanguage,
                        rippedcd.new.origyear
                    ]
                )
            )
            obj = list(set(obj))
            with open(DABJSON, WRITE) as fp:
                json.dump(sorted(obj, key=itemgetter(0)), fp, indent=4, sort_keys=True)
            obj.clear()

            #  --> 2. Audio CD ripping database.
            if exists(RIPDBJSON):
                with open(RIPDBJSON) as fp:
                    obj = json.load(fp)
                obj = [tuple(item) for item in obj]
            while True:
                obj.append(
                    tuple(
                        [
                            rippedcd.new.artist,
                            rippedcd.new.year,
                            album(rippedcd.new),
                            rippedcd.new.genre,
                            rippedcd.new.upc,
                            rippedcd.new.albumsort[:-3],
                            rippedcd.new.artistsort
                        ]
                    )
                )
                try:
                    obj = list(set(obj))
                except TypeError:
                    obj.clear()
                else:
                    break
            with open(RIPDBJSON, WRITE) as fp:
                json.dump(sorted(obj, key=itemgetter(0)), fp, indent=4, sort_keys=True)
            obj.clear()
