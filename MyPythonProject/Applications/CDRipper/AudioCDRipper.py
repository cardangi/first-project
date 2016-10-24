# -*- coding: ISO-8859-1 -*-
import os
import re
import json
import argparse
import logging.handlers
from pytz import timezone
from datetime import datetime
from operator import itemgetter
from contextlib import ContextDecorator
from jinja2 import Environment, FileSystemLoader
from .. import shared as s1
from .Modules import shared as s2

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
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ============
# Local names.
# ============
exists, join, expandvars = os.path.exists, os.path.join, os.path.expandvars


# ==========
# Constants.
# ==========
JSON, DABJSON, RIPDBJSON = join(expandvars("%TEMP%"), "tags.json"), join(expandvars("%TEMP%"), "digitalaudiodatabase.json"), join(expandvars("%TEMP%"), "rippinglog.json")


# ==========
# Variables.
# ==========
NewRippedCD, fo, encoding, obj, dab, regex, arguments = None, None, None, [], [], re.compile(s2.DFTPATTERN), parser.parse_args()


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "CDRipper", "Templates")), trim_blocks=True, lstrip_blocks=True)


# =================
# Jinja2 templates.
# =================
outputtags = environment.get_template("AudioCDOutputTags")


class MyClass(ContextDecorator):

    profiles = {"default": s2.DefaultCD.fromfile, "selftitled": s2.SelfTitledCD.fromfile}

    def __init__(self, profile, file):
        self.profile = profile
        self.file = file

    def __enter__(self):

        # 0.
        logger.info("{0:=^140}".format(" {0} ".format(s1.dateformat(datetime.now(tz=timezone(s1.DFTTIMEZONE)), s1.TEMPLATE1))))
        logger.info('START "%s".' % (os.path.basename(__file__),))
        logger.info('"{0}" used as ripping profile.'.format(arguments.rippingprofile))
        logger.info('#0029')

        # 1.
        logger.debug("Input file.")
        logger.debug('\t"{0}"'.format(self.file).expandtabs(4))
        logger.debug("Input tags.")
        if exists(self.file):
            with open(self.file, encoding=s1.UTF16) as fr:
                for line in fr:
                    logger.debug("\t{0}".format(line.splitlines()[0]).expandtabs(4))

        objj = None
        # 2.
        try:
            objj = self.profiles[self.profile](self.file, s1.UTF16)
        except ValueError as e:
            logger.debug(e)
        else:
            fo, encoding = self.file, s1.UTF16
            if arguments.test:
                fo, encoding = join(expandvars("%TEMP%"), "T{0}.txt".format(objj.tracknumber.zfill(2))), s1.UTF8
            with open(fo, s1.WRITE, encoding=encoding) as fw:
                logger.debug("Tags file.")
                logger.debug("\t{0}".format(fo).expandtabs(4))
                fw.write(outputtags.render(tags=objj))
        finally:
            return objj

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug(exc_type)
        logger.debug(exc_val)
        logger.debug(exc_tb)
        logger.info('END "%s".' % (os.path.basename(__file__),))

# ==============
# Start logging.
# ==============
# logger.info("{0:=^140}".format(" {0} ".format(s1.dateformat(datetime.now(tz=timezone(s1.DFTTIMEZONE)), s1.TEMPLATE1))))
# logger.info('START "%s".' % (os.path.basename(__file__),))
# logger.info('"{0}" used as ripping profile.'.format(arguments.rippingprofile))


# ===============
# Main algorithm.
# ===============
if exists(arguments.tagsfile) and arguments.rippingprofile.lower() in s2.PROFILES:

    with MyClass(arguments.rippingprofile, arguments.tagsfile) as NewRippedCD:

        if NewRippedCD:

            if exists(DABJSON):
                with open(DABJSON) as fp:
                    dab = json.load(fp)
                dab = [tuple(item) for item in dab]
            dab.append(
                tuple(
                    [
                        NewRippedCD.index,
                        NewRippedCD.albumsort[:-3],
                        NewRippedCD.titlesort,
                        NewRippedCD.artist,
                        NewRippedCD.year,
                        NewRippedCD.album,
                        NewRippedCD.genre,
                        NewRippedCD.discnumber,
                        NewRippedCD.totaldiscs,
                        NewRippedCD.label,
                        NewRippedCD.tracknumber,
                        NewRippedCD.totaltracks,
                        NewRippedCD.title,
                        NewRippedCD.live,
                        NewRippedCD.bootleg,
                        NewRippedCD.incollection,
                        NewRippedCD.upc,
                        NewRippedCD.encodingyear,
                        NewRippedCD.titlelanguage,
                        NewRippedCD.origyear
                    ]
                )
            )
            dab = list(set(dab))
            with open(DABJSON, s1.WRITE) as fp:
                json.dump(sorted(dab, key=itemgetter(0)), fp, indent=4, sort_keys=True)
            dab.clear()

            #  --> 2.b. Audio CD ripping database.
            if exists(RIPDBJSON):
                with open(RIPDBJSON) as fp:
                    dab = json.load(fp)
                dab = [tuple(item) for item in dab]
            while True:
                dab.append(
                    tuple(
                        [
                            NewRippedCD.artist,
                            NewRippedCD.year,
                            NewRippedCD.album,
                            NewRippedCD.genre,
                            NewRippedCD.upc,
                            NewRippedCD.albumsort[:-3],
                            NewRippedCD.artistsort
                        ]
                    )
                )
                try:
                    dab = list(set(dab))
                except TypeError:
                    dab.clear()
                else:
                    break
            with open(RIPDBJSON, s1.WRITE) as fp:
                json.dump(sorted(dab, key=itemgetter(0)), fp, indent=4, sort_keys=True)
            dab.clear()

    #        ----------------
    # --> 6. Log output tags.
    #        ----------------
            logger.debug("Output tags.")
            for k, v in NewRippedCD.items():
                logger.debug("\t{0}={1}".format(k, v).expandtabs(4))

    #        -----------------
    # --> 7. Stocker les tags.
    #        -----------------
            # Set output tags.
            # Default output is the input file encoded in "utf-16-le".
            # Test output is a temporary "IDTags.txt" file encoded in "utf-8".
            # fo, encoding = arguments.tagsfile, s1.UTF16
            # if arguments.test:
            #     fo, encoding = join(expandvars("%TEMP%"), "T{0}.txt".format(NewRippedCD.tracknumber.zfill(2))), s1.UTF8
            # with open(fo, s1.WRITE, encoding=encoding) as fw:
            #     logger.debug("Tags file.")
            #     logger.debug("\t{0}".format(fo).expandtabs(4))
            #     fw.write(outputtags.render(tags=NewRippedCD))

    #        ----------------------------------
    # --> 8. Stocker les tags au format python.
    #        ----------------------------------
            if exists(JSON):
                with open(JSON) as fp:
                    obj = json.load(fp)
            obj.append(dict(NewRippedCD))
            with open(JSON, s1.WRITE) as fp:
                json.dump(obj, fp, indent=4, sort_keys=True)


# ============
# End logging.
# ============
# logger.info('END "%s".' % (os.path.basename(__file__),))
