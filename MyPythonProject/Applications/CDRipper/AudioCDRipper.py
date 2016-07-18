# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import os
import re
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
def hasattribute(object, name):
    if hasattr(object, name):
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
# Variables.
# ==========
l, NewRippedCD, fo, encoding, regex, arguments = [], None, None, None, re.compile(s2.DFTPATTERN), parser.parse_args()


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=PackageLoader("Applications.CDRipper", "Templates"), trim_blocks=True, keep_trailing_newline=True)
environment.filters["hasattribute"] = hasattribute
outputtags = environment.get_template("AudioCDOutputTags")
rippinglog = environment.get_template("AudioCDRippingLog")
audiodatabase = environment.get_template("DigitalAudioBase")


# ==============
# Start logging.
# ==============
logger.info("{0} {1} {0}".format("="*50, s1.dateformat(datetime.now(tz=timezone(s1.DFTTIMEZONE)), s1.TEMPLATE1)))
logger.info('START "%s".' % (os.path.basename(__file__),))
logger.info('"{0}" used as ripping profile.'.format(arguments.profile))


# ===============
# Main algorithm.
# ===============
if exists(arguments.input) and arguments.profile.lower() in s2.PROFILES:

    #     ---------------
    # --> Log input tags.
    #     ---------------
    logger.debug("Input file.")
    logger.debug('\t"{0}"'.format(arguments.input).expandtabs(4))
    logger.debug("Input tags.")
    if exists(arguments.input):
        with open(arguments.input, encoding=s1.UTF16) as fr:
            for line in fr:
                logger.debug("\t{0}".format(line.splitlines()[0]).expandtabs(4))

    #     ----------------------------
    # --> Open connection to database.
    #     ----------------------------
    # conn = sqlite3.connect(s1.DATABASE)
    # conn.row_factory = sqlite3.Row

    #     -----------
    # --> Default CD.
    #     -----------
    if arguments.profile.lower() == s2.PROFILES[0]:
        NewRippedCD = s2.DefaultCD.fromfile(arguments.input, s1.UTF16)

        #          같같같같같같같같같같같�
        # ----- 1. Digital audio database.
        #          같같같같같같같같같같같�
        with open(join(expandvars("%TEMP%"), "digitalaudiodatabase.txt"), mode=s1.APPEND, encoding=s1.DFTENCODING) as fw:
            fw.write("{0}\n".format(audiodatabase.render(headers=[], rippedcd=NewRippedCD)))

        #          같같같같같같같같같같같같같
        # ----- 2. Audio CD ripping database.
        #          같같같같같같같같같같같같같
        with open(join(expandvars("%TEMP%"), "rippingdatabase"), mode=s1.APPEND, encoding=s1.DFTENCODING) as fw:
            fw.write("{0}\n".format(rippinglog.render(detail=list((NewRippedCD.artist, NewRippedCD.year, NewRippedCD.album, NewRippedCD.genre, NewRippedCD.upc, NewRippedCD.albumsort[:-3], NewRippedCD.tracknumber,
                                                                   NewRippedCD.encoder, NewRippedCD.artistsort)))))

    #     --------------
    # --> Soundtrack CD.
    #     --------------
    # elif arguments.profile.lower() == s2.PROFILES[1]:
    #     NewRippedCD = s2.SoundtrackCD.fromfile(arguments.input, s1.UTF16)

    #     ---------------
    # --> Self titled CD.
    #     ---------------
    elif arguments.profile.lower() == s2.PROFILES[3]:
        NewRippedCD = s2.SelfTitledCD.fromfile(arguments.input, s1.UTF16)

    #     -----------------------
    # --> Springsteen bootleg CD.
    #     -----------------------
    elif arguments.profile.lower() == s2.PROFILES[1]:
        NewRippedCD = s2.DefaultBootlegs.fromfile(arguments.input, s1.UTF16)

    #     ---------------------
    # --> Pearl Jam bootleg CD.
    #     ---------------------
    elif arguments.profile.lower() == s2.PROFILES[2]:
        NewRippedCD = s2.PJBootlegs.fromfile(arguments.input, s1.UTF16)

    #     -----------------------
    # --> Crystal Cat bootleg CD.
    #     -----------------------
    # elif arguments.profile.lower() == s2.PROFILES[6]:
    #     NewRippedCD = s2.DefaultBootlegs.fromfile(arguments.input, s1.UTF16)

    #     ------------------------
    # --> Other artist bootleg CD.
    #     ------------------------
    # elif arguments.profile.lower() == s2.PROFILES[5]:
    #     NewRippedCD = s2.DefaultBootlegs.fromfile(arguments.input, s1.UTF16)

    #     ----------------
    # --> Log output tags.
    #     ----------------
    logger.debug("Output tags.")
    for k, v in NewRippedCD:
        logger.debug("\t{0}={1}".format(k, v).expandtabs(4))

    #     --------------------------------
    # --> Elaboration du fichier des tags.
    #     --------------------------------
    # Set output tags.
    # Default output is the input file encoded in "utf-16-le".
    # Test output is a temporary "IDTags.txt" file encoded in "utf-8".
    fo, encoding = arguments.input, s1.UTF16
    if arguments.test:
        fo, encoding = join(expandvars("%TEMP%"), "OutTagsT{0}.txt".format(NewRippedCD.tracknumber.zfill(2))), s1.UTF8
    with open(fo, s1.WRITE, encoding=encoding) as fw:
        fw.write(outputtags.render(tags=NewRippedCD))

    #     ------------------------------------------------
    # --> Commit changes and close connection to database.
    #     ------------------------------------------------
    # conn.close()


# ============
# End logging.
# ============
logger.info('END "%s".' % (os.path.basename(__file__),))
