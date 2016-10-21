# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import os
import re
import json
import logging
import argparse
import logging.handlers
from pytz import timezone
from datetime import datetime
from jinja2 import Environment, PackageLoader


# =================
# Relative imports.
# =================
from .. import shared as s1
from .Modules import shared as s2


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("tagsfile", help="tags file")
parser.add_argument("rippingprofile", help="rip profile")
parser.add_argument("-t", "--test", action="store_true")


# ======================
# Jinja2 custom filters.
# ======================
def hasattribute(obj, attr):
    if hasattr(obj, attr):
        return True
    return False


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ============
# Local names.
# ============
exists, join, expandvars, missingattribute = os.path.exists, os.path.join, os.path.expandvars, s2.missingattribute


# ==========
# Constants.
# ==========
JSON, DABJSON = join(expandvars("%TEMP%"), "tags.json"), join(expandvars("%TEMP%"), "digitalaudiodatabase.json")


# ==========
# Variables.
# ==========
NewRippedCD, fo, encoding, obj, dab, regex, arguments = None, None, None, [], [], re.compile(s2.DFTPATTERN), parser.parse_args()


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=PackageLoader("Applications.CDRipper", "Templates"), trim_blocks=True, lstrip_blocks=True)


# ======================
# Jinja2 custom filters.
# ======================
environment.filters["hasattribute"] = hasattribute


# =================
# Jinja2 templates.
# =================
outputtags = environment.get_template("AudioCDOutputTags")
rippinglog = environment.get_template("AudioCDRippingLog")
audiodatabase = environment.get_template("DigitalAudioBase")


# ==============
# Start logging.
# ==============
logger.info("{0} {1} {0}".format("="*50, s1.dateformat(datetime.now(tz=timezone(s1.DFTTIMEZONE)), s1.TEMPLATE1)))
logger.info('START "%s".' % (os.path.basename(__file__),))
logger.info('"{0}" used as ripping profile.'.format(arguments.rippingprofile))


# ===============
# Main algorithm.
# ===============
if exists(arguments.tagsfile) and arguments.rippingprofile.lower() in s2.PROFILES:

    #     ---------------
    # --> Log input tags.
    #     ---------------
    logger.debug("Input file.")
    logger.debug('\t"{0}"'.format(arguments.tagsfile).expandtabs(4))
    logger.debug("Input tags.")
    if exists(arguments.tagsfile):
        with open(arguments.tagsfile, encoding=s1.UTF16) as fr:
            for line in fr:
                logger.debug("\t{0}".format(line.splitlines()[0]).expandtabs(4))

    #     -----------
    # --> Default CD.
    #     -----------
    if arguments.rippingprofile.lower() == s2.PROFILES[0]:
        NewRippedCD = s2.DefaultCD.fromfile(arguments.tagsfile, s1.UTF16)

        #          °°°°°°°°°°°°°°°°°°°°°°°
        # ----- 1. Digital audio database.
        #          °°°°°°°°°°°°°°°°°°°°°°°
        if exists(DABJSON):
            with open(DABJSON) as fp:
                dab = json.load(fp)
            dab = [tuple(item) for item in dab]
        dab.append(tuple(NewRippedCD.digitalaudiobase()))
        with open(JSON, s1.WRITE) as fp:
            json.dump(sorted(dab, key=itemgetter(0)), fp, indent=4, sort_keys=True)

        #          °°°°°°°°°°°°°°°°°°°°°°°°°°
        # ----- 2. Audio CD ripping database.
        #          °°°°°°°°°°°°°°°°°°°°°°°°°°
        with open(join(expandvars("%TEMP%"), "rippingdatabase"), mode=s1.APPEND, encoding=s1.DFTENCODING) as fw:
            fw.write("{0}\n".format(rippinglog.render(detail=list((NewRippedCD.artist, NewRippedCD.year, NewRippedCD.album, NewRippedCD.genre, NewRippedCD.upc, NewRippedCD.albumsort[:-3], NewRippedCD.tracknumber,
                                                                   NewRippedCD.encoder, NewRippedCD.artistsort)))))

    #     ---------------
    # --> Self titled CD.
    #     ---------------
    elif arguments.rippingprofile.lower() == s2.PROFILES[3]:
        NewRippedCD = s2.SelfTitledCD.fromfile(arguments.tagsfile, s1.UTF16)

    #     -----------------------
    # --> Springsteen bootleg CD.
    #     -----------------------
    elif arguments.rippingprofile.lower() == s2.PROFILES[1]:
        NewRippedCD = s2.DefaultBootlegs.fromfile(arguments.tagsfile, s1.UTF16)

    #     ---------------------
    # --> Pearl Jam bootleg CD.
    #     ---------------------
    elif arguments.rippingprofile.lower() == s2.PROFILES[2]:
        NewRippedCD = s2.PJBootlegs.fromfile(arguments.tagsfile, s1.UTF16)

    #     ----------------
    # --> Log output tags.
    #     ----------------
    logger.debug("Output tags.")
    for k, v in NewRippedCD.items():
        logger.debug("\t{0}={1}".format(k, v).expandtabs(4))

    #     -----------------
    # --> Stocker les tags.
    #     -----------------
    # Set output tags.
    # Default output is the input file encoded in "utf-16-le".
    # Test output is a temporary "IDTags.txt" file encoded in "utf-8".
    fo, encoding = arguments.tagsfile, s1.UTF16
    if arguments.test:
        fo, encoding = join(expandvars("%TEMP%"), "T{0}.txt".format(NewRippedCD.tracknumber.zfill(2))), s1.UTF8
    with open(fo, s1.WRITE, encoding=encoding) as fw:
        fw.write(outputtags.render(tags=NewRippedCD))

    #     ----------------------------------
    # --> Stocker les tags au format python.
    #     ----------------------------------
    if exists(JSON):
        with open(JSON) as fp:
            obj = json.load(fp)
    obj.append({key: NewRippedCD[key] for key in NewRippedCD})
    with open(JSON, s1.WRITE) as fp:
        json.dump(obj, fp, indent=4, sort_keys=True)


# ============
# End logging.
# ============
logger.info('END "%s".' % (os.path.basename(__file__),))
