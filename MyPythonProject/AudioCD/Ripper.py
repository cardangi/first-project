# -*- coding: ISO-8859-1 -*-
import os
import json
import yaml
import logging
import argparse
from operator import itemgetter
from contextlib import ExitStack
from logging.config import dictConfig
from Applications.shared import WRITE
from Applications.AudioCD.shared import RippedCD, album


__author__ = 'Xavier ROSSET'


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("file", help="tags file")
parser.add_argument("profile", help="rip profile")
parser.add_argument("-t", "--test", action="store_true")


# ========
# Logging.
# ========
logger = None
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml")) as fp:
    d = yaml.load(fp)
if d:
    dictConfig(d)
    if __name__ == "__main__":
        logger = logging.getLogger(os.path.basename(__file__))
    else:
        logger = logging.getLogger(__name__)


# ============
# Local names.
# ============
exists, join, expandvars = os.path.exists, os.path.join, os.path.expandvars


# ==========
# Constants.
# ==========
DADBJSON, CDDBJSON = join(expandvars("%TEMP%"), "digitalaudiodatabase.json"), join(expandvars("%TEMP%"), "rippinglog.json")


# ==========
# Variables.
# ==========
obj, arguments = [], parser.parse_args()


# ===============
# Main algorithm.
# ===============
stack = ExitStack()
try:
    rippedcd = stack.enter_context(RippedCD(arguments.profile, arguments.file, arguments.test))
except ValueError as e:
    logger.debug(e)
else:
    with stack:
        if rippedcd.profile in ["default", "selftitled"]:

            #  --> 1. Digital audio database.
            if exists(DADBJSON):
                with open(DADBJSON) as fp:
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
            with open(DADBJSON, WRITE) as fp:
                json.dump(sorted(obj, key=itemgetter(0)), fp, indent=4, sort_keys=True)
            obj.clear()

            #  --> 2. Audio CD ripping database.
            if exists(CDDBJSON):
                with open(CDDBJSON) as fp:
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
            with open(CDDBJSON, WRITE) as fp:
                json.dump(sorted(obj, key=itemgetter(0)), fp, indent=4, sort_keys=True)
            obj.clear()
