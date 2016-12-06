# -*- coding: utf-8 -*-
from Applications.AudioCD.shared import validdelay
from logging.config import dictConfig
from Applications.shared import UTF8
import argparse
import logging
import sched
import yaml
import sys
import os
import re

__author__ = 'Xavier ROSSET'


# ============
# Local names.
# ============
basename, dirname, exists, splitext = os.path.basename, os.path.dirname, os.path.exists, os.path.splitext


# ==========
# Functions.
# ==========
def validfolder(f):
    if not exists(f):
        raise argparse.ArgumentTypeError('"{0}" isn\'t a valid folder.'.format(f))
    return f


def updatetags(*extensions, folder=folder, test=True):

    logger = logging.getLogger("Default.{0}.updatetags".format(splitext(basename(__file__))[0]))
    rex = re.compile(r"^(?:{0})\.\d -\B".format(shared.DFTYEARREGEX))
    l = []

    for num, (fil, audioobj, tags) in enumerate(audiofilesinfolder(*extensions, folder=folder), start=1):
        if any(tag not in tags for tag in ["album", "albumsort"]):
            continue
        if rex.match(tags["album"]):
            continue
        album = "{0}.{1} - {2}".format(tags["albumsort"][2:6], tags["albumsort"][11], tags["album"])
        logger.debug('{0:>3d}. "{1}".'.format(num, fil))
        logger.debug('\t\tNew album: "{0}".'.format(album).expandtabs(5))
        if not test:
            if updatetags2(audioobj, album=album):
                logger.debug('\t"{0}" updated.'.format(fil).expandtabs(5))
                l.append(fil)

    if l:
        logger.debug("{0:>3d} file(s) updated.".format(len(l)))


def updatetags2(audioobj, **kwargs):

    try:
        for k, v in kwargs.items():
            audioobj[k] = v
        audioobj.save()
    except mutagen.MutagenError as err:
        logger.exception(err)
        return False
    return True

# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("folder", type=validfolder)
parser.add_argument("-d", "--delay", type=validdelay, default="0")
parser.add_argument("-t", "--test", action="store_true")


# ================
# Initializations.
# ================
arguments = parser.parse_args()


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding=UTF8) as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger("Ripper.{0}".format(os.path.splitext(os.path.basename(__file__))[0]))
logger.debug("Delay: {0} second(s).".format(arguments.delay))
logger.debug("Test : {0}.".format(arguments.test))


# ===============
# Main algorithm.
# ===============

# Mise à jour immédiate.
if not arguments.delay:
    updatetags("flac", "ape", folder=arguments.folder, test=arguments.test)
    sys.exit(0)

# Mise à jour différée.
s = sched.scheduler()
s.enter(arguments.delay, 1, updatetags, argument=("flac", "ape"), kwargs={"folder": arguments.folder, "test": arguments.test})
s.run()
