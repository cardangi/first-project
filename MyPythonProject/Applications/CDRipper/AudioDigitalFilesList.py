# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import re
import locale
import os.path
import argparse
from pytz import timezone
from datetime import datetime
from operator import itemgetter
from os.path import normpath, splitext
import xml.etree.ElementTree as ElementTree
from sortedcontainers import SortedDict, SortedList


# =================
# Relative imports.
# =================
from Applications import shared


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Functions.
# ==========
def canfilebeprocessed(fe, *tu):
    """
    fe: file extension.
    tu: filtered extensions tuple.
    """
    if not tu:
        return True
    if tu:
        if fe.lower() in tu:
            return True
    return False


def directory(d):
    if not os.path.isdir(d):
        raise argparse.ArgumentTypeError('"{}" is not a valid directory'.format(d))
    if not os.access(d, os.R_OK):
        raise argparse.ArgumentTypeError('"{}" is not a readable directory'.format(d))
    return d


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="mandatory directory to walk through", type=directory)
parser.add_argument("-e", "--ext", dest="extension", help="one or more extension(s) to filter out", nargs="*")
arguments = parser.parse_args()


# ================
# Initializations.
# ================
reflist, lista, listb, listc, listd, liste, extensions, artists, rex1, rex2, acount, ecount = [], [], [], [], [], [], SortedDict(), SortedDict(), \
                                                                                              re.compile(r"^(?:[^\\]+\\){2}([^\\]+)\\"), re.compile("recycle", re.IGNORECASE), \
                                                                                              0, 0


# ===============
# Main algorithm.
# ===============
for fil in shared.directorytree(normpath(arguments.directory)):
    match = rex2.search(fil)
    if not match:
        art = None
        ext = None
        if canfilebeprocessed(splitext(fil)[1][1:], *tuple(arguments.extension)):
            ext = splitext(fil)[1][1:].upper()
            match = rex1.match(normpath(fil))
            if match:
                reflist.append((fil, int(os.path.getctime(fil)), "Créé le %s" % (shared.dateformat(datetime.fromtimestamp(os.path.getctime(fil), tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1),), len(fil)))
                art = match.group(1)
        if ext:
            if ext not in extensions:
                extensions[ext] = 0
            extensions[ext] += 1
            ecount += 1
        if art:
            if art not in artists:
                artists[art] = 0
            artists[art] += 1
            acount += 1


#    ------
# 1. Files.
#    ------
if reflist:

    # ----- Liste des fichiers. Tri par nom croissant.
    templist1 = [i for i in range(1, len(reflist) + 1)]
    templist2 = [fil for fil, dummy1, dummy2, dummy3 in SortedList(reflist)]
    templist3 = [humantime for dummy1, dummy2, humantime, dummy3 in SortedList(reflist)]
    lista = list(zip(templist1, templist2, templist3))

    # ----- Liste des 50 fichiers créés dernièrement. Tri par date décroissante, puis nom croissant.
    templist1 = [i for i in range(1, 51)]
    templist2 = [fil for fil, dummy1, dummy2 in sorted([(fil, epoch, humantime) for fil, epoch, humantime, dummy1 in sorted(reflist, key=itemgetter(0))], key=itemgetter(1), reverse=True)[:50]]
    templist3 = [humantime for dummy1, dummy2, humantime in sorted([(fil, epoch, humantime) for fil, epoch, humantime, dummy1 in sorted(reflist, key=itemgetter(0))], key=itemgetter(1), reverse=True)[:50]]
    listb = list(zip(templist1, templist2, templist3))


#    -----------
# 2. Extensions.
#    -----------
if extensions:
    templist1 = [i for i in range(1, len(extensions) + 1)]
    templist2 = [key for key in sorted(list(extensions.keys()))]
    templist3 = [extensions[key] for key in sorted(list(extensions.keys()))]
    listc = list(zip(templist1, templist2, templist3))


#    --------
# 3. Artists.
#    --------
if artists:

    templist1 = [i for i in range(1, len(artists) + 1)]

    templist2 = [key for key in sorted(list(artists.keys()))]
    templist3 = [artists[key] for key in sorted(list(artists.keys()))]
    listd = list(zip(templist1, templist2, templist3))

    templist2 = [artist for artist, dummy in sorted([(key, artists[key]) for key in sorted(list(artists.keys()))], key=itemgetter(1), reverse=True)]
    templist3 = [count for dummy, count in sorted([(key, artists[key]) for key in sorted(list(artists.keys()))], key=itemgetter(1), reverse=True)]
    liste = list(zip(templist1, templist2, templist3))


#    -----------
# 4. XML Output.
#    -----------
root = ElementTree.Element("Data", attrib=dict(css="firstcss.css"))
if lista:
    d1 = ElementTree.SubElement(root, "Details")
    for item1, item2, item3 in lista:
        file = ElementTree.SubElement(d1, "File", attrib=dict(number=str(item1), created=item3))
        file.text = item2
if listb:
    d2 = ElementTree.SubElement(root, "RecentFiles")
    for item1, item2, item3 in listb:
        file = ElementTree.SubElement(d2, "File", attrib=dict(number=str(item1), created=item3))
        file.text = item2
if listc:
    d3 = ElementTree.SubElement(root, "Extensions")
    for item1, item2, item3 in listc:
        file = ElementTree.SubElement(d3, "Extension", attrib=dict(number=str(item1), count=str(item3)))
        file.text = item2
if listd:
    d4 = ElementTree.SubElement(root, "Artists")
    for item1, item2, item3 in listd:
        file = ElementTree.SubElement(d4, "Artist", attrib=dict(number=str(item1), count=str(item3)))
        file.text = item2
if liste:
    d5 = ElementTree.SubElement(root, "Artists2")
    for item1, item2, item3 in liste:
        file = ElementTree.SubElement(d5, "Artist", attrib=dict(number=str(item1), count=str(item3)))
        file.text = item2
if any([lista, listb, listc, listd, liste]):
    ElementTree.ElementTree(root).write(os.path.join(os.path.expandvars("%_COMPUTING%"), "AudioDigitalFilesList.xml"), encoding="UTF-8", xml_declaration=True)



