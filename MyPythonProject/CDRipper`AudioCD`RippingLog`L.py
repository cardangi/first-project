# -*- coding: ISO-8859-1 -*-
import os
import sys
import json
import operator
import subprocess
from operator import itemgetter
from contextlib import contextmanager

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
@contextmanager
def chgcurdir(d):
    wcdir = os.getcwd()
    os.chdir(d)
    yield
    os.chdir(wcdir)


# ==========
# Constants.
# ==========
CURDIR, JSON = os.path.expandvars("%_PYTHONPROJECT%"), os.path.join(os.path.expandvars("%TEMP%"), "rippinglog.json")


# ================
# Initializations.
# ================
tags, returncodes, dftcmd = [], [], [r"C:\Program Files (x86)\Python35-32\python.exe", "-m", "Applications.CDRipper.AudioCD`RippingLog", "insert"]


# ===============
# Main algorithm.
# ===============
if os.path.exists(JSON):
    with open(JSON) as fp:
        for artist, year, album, genre, upc, albumsort, artistsort in json.load(fp):
            cmd = list(dftcmd)
            cmd.append(artist)
            cmd.append(year)
            cmd.append(album)
            cmd.append(genre)
            cmd.append(upc)
            cmd.append(albumsort)
            cmd.append(artistsort)
            with chgcurdir(CURDIR):
                process = subprocess.run(cmd)
                returncodes.append(process.returncode)


# ===============
# Exit algorithm.
# ===============
if not returncodes:
    sys.exit(99)
if all([not(operator.eq(i, 0)) for i in returncodes]):
    sys.exit(98)
if any([not(operator.eq(i, 0)) for i in returncodes]):
    sys.exit(97)
sys.exit(0)
