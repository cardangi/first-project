# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import os
from jinja2 import Environment, PackageLoader


# =================
# Relative imports.
# =================
from Applications import shared as s1


# ============
# Local names.
# ============
join, expandvars = os.path.join, os.path.expandvars


# ======================
# Jinja2 custom filters.
# ======================
def hasattribute(object, name):
    if hasattr(object, name):
        return True
    return False


# ==========
# Constants.
# ==========
HEADERS = ["index", "albumsort", "titlesort", "artist", "year", "album", "genre", "discnumber", "totaldiscs", "publisher", "track", "totaltracks", "title", "live", "bootleg", "incollection", "upc", "encodingyear",
           "language", "origyear"]


# ================
# Initializations.
# ================
class NewRippedCD:
    pass


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=PackageLoader("Applications.CDRipper", "Templates"), trim_blocks=True)
environment.filters["hasattribute"] = hasattribute
audiodatabase = environment.get_template("displayDigitalAudioBase")


# ===============
# Main algorithm.
# ===============
rippedcd = NewRippedCD()
rippedcd.albumartistsort = "Springsteen, Bruce"
rippedcd.albumsort = "1.20150000.1.13"
rippedcd.titlesort = "D1.T01"
rippedcd.artist = "Bruce Springsteen"
rippedcd.year = "2015"
rippedcd.album = "The Ties that Bind"
rippedcd.genre = "Rock"
rippedcd.discnumber = "1"
rippedcd.totaldiscs = "6"
rippedcd.label = ""
rippedcd.tracknumber = "10"
rippedcd.totaltracks = "22"
rippedcd.title = "Cindy"
rippedcd.live = "N"
rippedcd.bootleg = "N"
rippedcd.incollection = "Y"
rippedcd.upc = ""
rippedcd.encodingyear = "2016"
rippedcd.titlelanguage = "English"
rippedcd.origyear = ""
with open(join(expandvars("%temp%"), "audiotags.txt"), mode=s1.WRITE, encoding=s1.DFTENCODING) as fw:
    fw.write("{0}\n".format(audiodatabase.render(headers=HEADERS, rippedcd=rippedcd)))
