# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from sortedcontainers import SortedDict
from datetime import datetime
from string import Template
from pytz import timezone
import argparse
import logging
import shutil
import csv
import os
import re


# =================
# Relative imports.
# =================
from Applications import shared


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ==========
# Constants.
# ==========
HEADERS = ["tag", "value"]
EXCLUDED = ["year", "disc", "track", "album artist", "description"]
PROFILES = ["pearl jam", "springsteen"]
DFTCOUNTRY = "United States"
PEARLJAM = Template("Live: $ccyy-$mm-$dd - $city")
SPRINGSTEEN = Template("$ccyy.$mm.$dd - [$city]")
ALBUMSORT = Template("2.$ccyy$mm$dd.1.$codec")
BOOTLEGTRACKYEAR = Template("$ccyy-$mm-$dd")
OUTPUT = Template("$key=$value")
ALBUMARTIST = {"springsteen": "Bruce Springsteen And The E Street Band"}
ARTISTSORT = {"springsteen": "Springsteen, Bruce"}
ARTIST = {"springsteen": "Bruce Springsteen"}
FLAC = 13
REGEX1 = r"^({0})/({1})/({2})\b ([^,]+,\B \w{{2}})$"
REGEX2 = r"^({0})/({1})/({2})\b (([^,]+),\B (\w{{3,}}))$"
REGEX3 = r"/\d{1,2}"
REGEX4 = r"^(\d\d?)(/(\d\d?))?$"
REGEX5 = r"powered by (.+)$"


# ==========
# Functions.
# ==========
def existingfile(f):
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError('"{0}" is not a valid file'.format(f))
    if not os.path.isfile(f):
        raise argparse.ArgumentTypeError('"{0}" is not a valid file'.format(f))
    if not os.access(f, os.R_OK):
        raise argparse.ArgumentTypeError('"{0}" is not a readable file'.format(f))
    return f


def existingprofile(p):
    if p.lower() not in PROFILES:
        raise argparse.ArgumentTypeError('"{0}" is not a valid profile'.format(p))
    return p


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("input", help="tags file", type=existingfile)
parser.add_argument("profile", help="tags profile", type=existingprofile)


# ================
# Initializations.
# ================
arguments = parser.parse_args()
d = {}


# ====================
# Regular expressions.
# ====================
rex1, rex2, rex3, rex4, rex5 = re.compile(REGEX1.format(shared.DFTYEARREGEX, shared.DFTMONTHREGEX, shared.DFTDAYREGEX), re.IGNORECASE), \
                               re.compile(REGEX2.format(shared.DFTYEARREGEX, shared.DFTMONTHREGEX, shared.DFTDAYREGEX), re.IGNORECASE), \
                               re.compile(REGEX3), \
                               re.compile(REGEX4), \
                               re.compile(REGEX5, re.IGNORECASE)


# ==============
# Start logging.
# ==============
logger.info("{0:=^138}".format(" {0} ".format(shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1))))
logger.info('START "%s".' % (os.path.basename(__file__),))


# ===============
# Main algorithm.
# ===============

#     ----------
#  1. Read tags.
#     ----------
with open(arguments.input, encoding=shared.UTF16) as fr:
    reader = csv.DictReader(fr, delimiter="=", fieldnames=HEADERS)
    for row in reader:
        d[row["tag"].strip().strip(shared.UTF16BOM).lower()] = row["value"].strip()
d = SortedDict(d)

#     ----------
#  2. Copy file.
#     ----------
#     For test or debug purpose.
disc = d["disc"]
match = rex4.match(d["disc"])
if match:
    disc = match.group(1)
track = d["track"]
match = rex4.match(d["track"])
if match:
    track = match.group(1)
shutil.copy(src=arguments.input, dst=os.path.join(os.path.expandvars("%temp%"), "Tags.D{0}.T{1}.txt".format(disc, track.zfill(2))))

#     --------
#  3. Logging.
#     --------
width = max([len(key) for key in sorted(d.keys())])
logger.debug("")
logger.debug("")
logger.debug("----------")
logger.debug("INPUT TAGS")
logger.debug("----------")
for key in sorted(d.keys()):
    logger.debug("{0:.<{1}}: {2}".format(key, width+1, d[key]))

#     -----
#  4. DATE.
#     -----
d["date"] = d["year"]

#     -----------
#  5. DISCNUMBER.
#     -----------
d["discnumber"] = disc

#     ------------
#  6. TRACKNUMBER.
#     ------------
d["tracknumber"] = track

#     ------------
#  7. TAGGINGTIME.
#     ------------
d["taggingtime"] = shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3)

#     ----------
#  8. TITLESORT.
#     ----------
d["titlesort"] = rex3.sub("", "D{0}.T{1}.NYY".format(d["discnumber"], d["tracknumber"].zfill(2)))

#     -------------
#  9. PURCHASEDATE.
#     -------------
d["purchasedate"] = datetime.now(tz=timezone(shared.DFTTIMEZONE)).strftime("%Y-%m-%d")

#     --------------
# 10. TITLELANGUAGE.
#     --------------
d["titlelanguage"] = "English"

#     -----------
# 11. ARTISTSORT.
#     -----------
d["artistsort"] = ARTISTSORT[arguments.profile.lower()]

#     ----------------
# 12. ALBUMARTISTSORT.
#     ----------------
d["albumartistsort"] = ARTISTSORT[arguments.profile.lower()]

#     ------------
# 13. ALBUMARTIST.
#     ------------
d["albumartist"] = ALBUMARTIST[arguments.profile.lower()]

#     -------
# 14. ARTIST.
#     -------
d["artist"] = ARTIST[arguments.profile.lower()]

#     --------------
# 15. MEDIAPROVIDER.
#     --------------
m5 = rex5.search(d["description"])
if m5:
    d["source"] = "Online provider"
    d["mediaprovider"] = m5.group(1)

#     ----------
# 16. DISCTOTAL.
#     ----------
d["disctotal"] = 3

#     ------------
# 16. Others tags.
#     ------------
m1 = re.match(rex1, d["album"])
m2 = re.match(rex2, d["album"])
if any([m1, m2]):

    if m1:
        # if arguments.profile.lower() == "pearl jam":
            # d["album"] = PEARLJAM.substitute(ccyy=m1.group(1), mm=m1.group(2), dd=m1.group(3), city=m1.group(4))
        if arguments.profile.lower() == "springsteen":
            d["album"] = SPRINGSTEEN.substitute(ccyy=m1.group(1), mm=m1.group(2), dd=m1.group(3), city=m1.group(4))
        d["albumsort"] = ALBUMSORT.substitute(ccyy=m1.group(1), mm=m1.group(2), dd=m1.group(3), codec=FLAC)
        d["bootlegtrackyear"] = BOOTLEGTRACKYEAR.substitute(ccyy=m1.group(1), mm=m1.group(2), dd=m1.group(3))
        d["bootlegtrackcity"] = m1.group(4)
        d["bootlegtrackcountry"] = DFTCOUNTRY
#
    if m2:
        # if arguments.profile.lower() == "pearl jam":
            # d["album"] = PEARLJAM.substitute(ccyy=m2.group(1), mm=m2.group(2), dd=m2.group(3), city=m2.group(4))
        if arguments.profile.lower() == "springsteen":
            d["album"] = SPRINGSTEEN.substitute(ccyy=m1.group(1), mm=m1.group(2), dd=m1.group(3), city=m1.group(4))
        d["albumsort"] = ALBUMSORT.substitute(ccyy=m2.group(1), mm=m2.group(2), dd=m2.group(3), codec=FLAC)
        d["bootlegtrackyear"] = BOOTLEGTRACKYEAR.substitute(ccyy=m2.group(1), mm=m2.group(2), dd=m2.group(3))
        d["bootlegtrackcity"] = m2.group(5)
        d["bootlegtrackcountry"] = m2.group(6)

#     -----------
# 17. Write tags.
#     -----------
with open(arguments.input, mode="w", encoding=shared.UTF16) as fw:
    logger.debug("")
    logger.debug("")
    logger.debug("-----------")
    logger.debug("OUTPUT TAGS")
    logger.debug("-----------")
    for k, v in d.items():
        if k not in EXCLUDED:
            fw.write("%s\n" % (OUTPUT.substitute(key=k, value=v),))
            logger.debug("{0:.<{1}}: {2}".format(k, width+1, v))


# ============
# End logging.
# ============
logger.debug("")
logger.debug("")
logger.info('END "%s".' % (os.path.basename(__file__),))
