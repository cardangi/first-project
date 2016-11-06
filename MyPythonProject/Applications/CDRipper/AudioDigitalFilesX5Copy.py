# -*- coding: ISO-8859-1 -*-
import mutagen.flac
import argparse
import logging
import json
import os
import re

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def validdrive(d):
    if not os.path.exists(d):
        raise argparse.ArgumentTypeError('"{0}" isn\'t a valid drive.'.format(d))
    return d


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("file", type=argparse.FileType(mode="rb"))
parser.add_argument("drive", type=validdrive)


# =========
# Contants.
# =========
JSON, TABSIZE = os.path.join(os.path.expandvars("%TEMP%"), "arguments.json"), 3


# ================
# Initializations.
# ================
x, y, arguments = [], [], parser.parse_args()


# ====================
# Regular expressions.
# ====================
rex1 = re.compile(r"((?:[^\\]+\\){3})", re.IGNORECASE)
rex2 = re.compile(r"[a-z]:", re.IGNORECASE)


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))
logger.debug("File.")
logger.debug("\t{0}".format(arguments.file.name).expandtabs(TABSIZE))


# ===============
# Main algorithm.
# ===============
try:
    audio = mutagen.flac.FLAC(arguments.file)
except mutagen.MutagenError:
    logger.debug('"{0}" is not a valid FLAC file.'.format(arguments.file.name))
else:
    logger.debug("Tags.")
    logger.debug("\tAlbumSort: {0}".format(audio["albumsort"][0][:-3]).expandtabs(TABSIZE))
    logger.debug("\tDisc     : {0}".format(audio.get("disc", audio["discnumber"])[0]).expandtabs(TABSIZE))
    logger.debug("\tTrack    : {0}".format(audio.get("track", audio["tracknumber"])[0]).expandtabs(TABSIZE))
    logger.debug("\tTitle    : {0}".format(audio["title"][0]).expandtabs(TABSIZE))
    if os.path.exists(JSON):
        with open(JSON) as fp:
            x = json.load(fp)
    match = rex1.match(arguments.file.name)
    if match:
        dst = os.path.normpath(os.path.join(rex2.sub(arguments.drive, match.group(1)), audio["albumsort"][0][:-3], "{0}.{1}.{2}{3}".format(audio.get("disc", audio["discnumber"])[0],
                                                                                                                                           audio.get("track", audio["tracknumber"])[0].zfill(2),
                                                                                                                                           audio["title"][0],
                                                                                                                                           os.path.splitext(arguments.file.name)[1]
                                                                                                                                           )
                                            )
                               )
        y = [(arguments.file.name, dst)]
    if y:
        x.extend(y)
    if x:
        with open(JSON, mode="w") as fp:
            json.dump(x, fp, indent=4)
