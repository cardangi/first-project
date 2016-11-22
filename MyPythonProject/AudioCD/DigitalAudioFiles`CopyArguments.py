# -*- coding: ISO-8859-1 -*-
"""
Stocker dans un fichier JSON les arguments permettant de copier un fichier audio FLAC reçu en qualité de premier paramètre.
La lettre identifiant le lecteur reçevant le fichier copié est reçue en qualité de deuxième paramètre.
Le nom du fichier JSON est reçu en qualité de troisième paramètre.
Le répertoire et le nom du fichier copié sont fonction des metadata "albumsort", "disc", "track" et "title".
"""
from logging.config import dictConfig
import mutagen.flac
import argparse
import logging
import yaml
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
parser.add_argument("file", type=argparse.FileType(mode="rb", encoding="UTF_8"))
parser.add_argument("drive", type=validdrive)
parser.add_argument("-o", "--out", dest="outjsonfile", default=os.path.join(os.path.expandvars("%TEMP%"), "arguments.json"))


# =========
# Contants.
# =========
TABSIZE = 3


# ================
# Initializations.
# ================
args, arguments = [], parser.parse_args()


# ====================
# Regular expressions.
# ====================
rex1 = re.compile(r"((?:[^\\]+\\){3})", re.IGNORECASE)
rex2 = re.compile(r"[a-z]:", re.IGNORECASE)


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])


# ===============
# Main algorithm.
# ===============
try:
    audio = mutagen.flac.FLAC(arguments.file)
except mutagen.MutagenError:
    pass
    logger.debug('"{0}" is not a valid FLAC file.'.format(arguments.file.name))
else:
    logger.debug("Tags.")
    logger.debug("\tAlbumSort: {0}".format(audio["albumsort"][0][:-3]).expandtabs(TABSIZE))
    logger.debug("\tDisc     : {0}".format(audio.get("disc", audio["discnumber"])[0]).expandtabs(TABSIZE))
    logger.debug("\tTrack    : {0}".format(audio.get("track", audio["tracknumber"])[0]).expandtabs(TABSIZE))
    logger.debug("\tTitle    : {0}".format(audio["title"][0]).expandtabs(TABSIZE))
    if os.path.exists(arguments.outjsonfile):
        with open(arguments.outjsonfile, encoding="UTF_8") as fp:
            args = json.load(fp)
    match = rex1.match(arguments.file.name)
    if match:
        dst = os.path.normpath(os.path.join(rex2.sub(arguments.drive, match.group(1)), audio["albumsort"][0][:-3], "{0}.{1}.{2}{3}".format(audio.get("disc", audio["discnumber"])[0],
                                                                                                                                           audio.get("track", audio["tracknumber"])[0].zfill(2),
                                                                                                                                           audio["title"][0],
                                                                                                                                           os.path.splitext(arguments.file.name)[1]
                                                                                                                                           )
                                            )
                               )
        args.extend([(arguments.file.name, dst)])
    if args:
        with open(arguments.outjsonfile, mode="w", encoding="UTF_8") as fp:
            json.dump(args, fp, indent=4)
            logger.debug("Copy arguments written.")

