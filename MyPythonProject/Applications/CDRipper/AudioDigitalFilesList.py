# -*- coding: utf-8 -*-
import re
import json
import locale
import os.path
import argparse
import collections
from pytz import timezone
from datetime import datetime
from operator import itemgetter
from os.path import normpath, splitext
import xml.etree.ElementTree as ElementTree
from sortedcontainers import SortedDict
from .. import shared as s1
from .Modules import shared as s2

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Functions.
# ==========
def isvaliddirectory(d):
    if not os.path.isdir(d):
        raise argparse.ArgumentTypeError('"{0}" is not a valid directory'.format(d))
    if not os.access(d, os.R_OK):
        raise argparse.ArgumentTypeError('"{0}" is not a readable directory'.format(d))
    return d


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="mandatory directory to walk through", type=isvaliddirectory)
parser.add_argument("-e", "--ext", dest="extension", help="one or more extension(s) to filter out", nargs="*")
arguments = parser.parse_args()


# ==========
# Constants.
# ==========
OUTFILE = os.path.join(os.path.expandvars("%TEMP%"), "ranking.json")

# ================
# Initializations.
# ================
reflist, lista, listb, listc, listd, liste, ext_list, art_list, artext_dict, extensions, artists, ext_count, art_count = [], [], [], [], [], [], [], [], SortedDict(), SortedDict(), SortedDict(), \
                                                                                                                         collections.Counter(), collections.Counter()
rex1, rex2 = re.compile(r"^(?:[^\\]+\\){2}([^\\]+)\\"), re.compile("recycle", re.IGNORECASE)


# ===============
# Main algorithm.
# ===============


#     ------------------------
#  1. Inventaire des fichiers.
#     ------------------------
for fil in s1.directorytree(normpath(arguments.directory)):
    match = rex2.search(fil)
    if not match:
        art = None
        ext = None
        ext_filter = arguments.extension
        if not ext_filter:
            ext_filter = []
        if s2.canfilebeprocessed(splitext(fil)[1][1:], *tuple(ext_filter)):
            ext = splitext(fil)[1][1:].upper()
            match = rex1.match(normpath(fil))
            if match:
                reflist.append((fil, int(os.path.getctime(fil)), "Créé le %s" % (s1.dateformat(datetime.fromtimestamp(os.path.getctime(fil), tz=timezone(s1.DFTTIMEZONE)), s1.TEMPLATE1),), len(fil)))
                art = match.group(1)
        if ext:
            ext_list.append(ext)
        if art:
            art_list.append(art)
        if all([art, ext]):
            if art not in artext_dict:
                artext_dict[art] = list()
            artext_dict[art].append(ext)


#     --------------------
#  2. Total par extension.
#     --------------------
for extension in ext_list:
    ext_count[extension] += 1

#  Tri par nom croissant.
ext_count1 = collections.OrderedDict(sorted(ext_count.items(), key=itemgetter(0)))

#  Tri par total décroissant et par nom croissant.
ext_count2 = collections.OrderedDict(sorted(sorted(ext_count.items(), key=itemgetter(0)), key=itemgetter(1), reverse=True))


#     ------------------
#  3. Total par artiste.
#     ------------------
for artist in art_list:
    art_count[artist] += 1

#  Tri par nom croissant.
art_count1 = collections.OrderedDict(sorted(art_count.items(), key=itemgetter(0)))

#  Tri par total décroissant et par nom croissant.
art_count2 = collections.OrderedDict(sorted(sorted(art_count.items(), key=itemgetter(0)), key=itemgetter(1), reverse=True))


#     -----------------------------------
#  4. Total par couple artiste/extension.
#     -----------------------------------

#  Total des extensions respectives à chaque artiste.
for artist in artext_dict.keys():
    artext_count = collections.Counter()
    for extension in artext_dict[artist]:
        artext_count[extension] += 1
    artext_dict[artist] = artext_count

#  Tri par extension croissante.
for artist in artext_dict.keys():
    artext_dict[artist] = collections.OrderedDict(sorted(artext_dict[artist].items(), key=itemgetter(0)))

#     ------
#  4. Files.
#     ------
if reflist:

    # ----- Liste des fichiers. Tri par nom croissant.
    lista = [(a, b, c) for a, (b, c) in enumerate([(itemgetter(0)(item), itemgetter(2)(item)) for item in sorted(reflist, key=itemgetter(0))], 1)]

    # ----- Liste des 50 fichiers créés dernièrement. Tri par date décroissante, puis nom croissant.
    listb = [(a, b, c) for a, (b, c) in enumerate([(itemgetter(0)(item), itemgetter(2)(item)) for item in sorted(sorted(reflist, key=itemgetter(0)), key=itemgetter(1), reverse=True)[:50]], 1)]


#     -----------
#  5. Extensions.
#     -----------
if extensions:
    listc = [(a, b, c) for a, (b, c) in enumerate([(itemgetter(0)(item), itemgetter(1)(item)) for item in sorted(extensions.items(), key=itemgetter(0))], 1)]


#     --------
#  6. Artists.
#     --------
if artists:

    # ----- Liste des artistes. Tri par nom croissant.
    listd = [(a, b, c) for a, (b, c) in enumerate([(itemgetter(0)(item), itemgetter(1)(item)) for item in sorted(artists.items(), key=itemgetter(0))], 1)]

    # ----- Liste des artistes. Tri par ranking décroissant, puis nom croissant.
    liste = [(a, b, c) for a, (b, c) in enumerate([(itemgetter(0)(item), itemgetter(1)(item)) for item in sorted(sorted(artists.items(), key=itemgetter(0)), key=itemgetter(1), reverse=True)], 1)]


#     -----------
#  7. XML Output.
#     -----------
root = ElementTree.Element("Data", attrib=dict(css="firstcss.css"))
if lista:
    se = ElementTree.SubElement(root, "Files")
    for item1, item2, item3 in lista:
        file = ElementTree.SubElement(se, "File", attrib=dict(number=str(item1), created=item3))
        file.text = item2
if listb:
    se = ElementTree.SubElement(root, "RecentFiles")
    for item1, item2, item3 in listb:
        file = ElementTree.SubElement(se, "File", attrib=dict(number=str(item1), created=item3))
        file.text = item2
if listc:
    se = ElementTree.SubElement(root, "Extensions")
    for item1, item2, item3 in listc:
        file = ElementTree.SubElement(se, "Extension", attrib=dict(number=str(item1), count=str(item3)))
        file.text = item2
if listd:
    se = ElementTree.SubElement(root, "Artists")
    for item1, item2, item3 in listd:
        file = ElementTree.SubElement(se, "Artist", attrib=dict(number=str(item1), count=str(item3)))
        file.text = item2
if liste:
    se = ElementTree.SubElement(root, "Ranking")
    for item1, item2, item3 in liste:
        file = ElementTree.SubElement(se, "Artist", attrib=dict(number=str(item1), count=str(item3)))
        file.text = item2
if any([lista, listb, listc, listd, liste]):
    ElementTree.ElementTree(root).write(os.path.join(os.path.expandvars("%_COMPUTING%"), "AudioDigitalFilesList.xml"), encoding="UTF-8", xml_declaration=True)


#     ---------------
#  8. Ranking Output.
#     ---------------
if any([ext_count1, ext_count2, art_count1, art_count2, artext_dict]):
    with open(OUTFILE, mode=s1.WRITE, encoding=s1.UTF8) as fp:
        json.dump([s1.now(), ext_count1, ext_count2, art_count1, art_count2, artext_dict], fp, indent=4)
