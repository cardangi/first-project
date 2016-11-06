# -*- coding: ISO-8859-1 -*-
import mutagen.flac
import argparse
import logging
import os

__author__ = 'Xavier ROSSET'


parser = argparse.ArgumentParser()
parser.add_argument("file", type=argparse.FileType(mode="rb"))
arguments = parser.parse_args()

logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))
logger.debug(arguments.file.name)
try:
    audio = mutagen.flac.FLAC(arguments.file)
except mutagen.MutagenError:
    logger.debug("KO")
else:
    logger.debug(audio["albumsort"][0][:-3])
    logger.debug(audio.get("disc", audio["discnumber"])[0])
    logger.debug(audio.get("track", audio["tracknumber"])[0])
    logger.debug(audio["title"][0])
