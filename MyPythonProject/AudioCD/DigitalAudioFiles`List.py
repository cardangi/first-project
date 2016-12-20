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
from Applications import shared
from os.path import normpath, splitext
from sortedcontainers import SortedDict
import xml.etree.ElementTree as ElementTree

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ========
# Classes.
# ========
class Interface(object):

        _regex = re.compile(r"\W+")
        _inputs = [("Please enter directory to walk through", "directory"),
                   ("Please enter extension(s) to filter out", "extensions")]

    def __init__(self):
        self._index, self._step = 0, 0
        self._extensions = None
        self._directory = None
        self._arguments = []

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._inputs):
            raise StopIteration
        if self._uid:
            raise StopIteration
        self._index += 1
        self._step += 1
        return self._inputs[self._index - 1]

    # -----
    # STEP.
    # -----
    @property
    def step(self):
        return self._step

    # ----------
    # ARGUMENTS.
    # ----------
    @property
    def arguments(self):
        return self._arguments

    # ----------
    # DIRECTORY.
    # ----------
    @property
    def directory(self):
        return self._directory

    @directory.setter
    def directory(self, arg):
        if not os.path.isdir(arg):
            raise ValueError('"{0}" is not a valid directory'.format(arg))
        if not os.access(d, os.R_OK):
            raise ValueError('"{0}" is not a readable directory'.format(arg))
        self._directory = arg
        self._arguments.append(arg)

    # -----------
    # EXTENSIONS.
    # -----------
    @property
    def extensions(self):
        return self._extensions

    @extensions.setter
    def extensions(self, arg):
        if arg:
            self._extensions = arg
            self._arguments.extend(self._regex.split(arg))


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="mandatory directory to walk through", type=isvaliddirectory)
parser.add_argument("extensions", help="one or more extension(s) to filter out", nargs="*")
arguments = parser.parse_args()


# ==========
# Constants.
# ==========
OUTFILE = os.path.join(os.path.expandvars("%TEMP%"), "ranking.json")


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":


    #     ---------------- 
    #  0. Initializations.
    #     ---------------- 
    reflist, lista, listb, listc, listd, liste, ext_list, art_list, artext_dict, extensions, artists = [], None, None, None, None, None, [], [], SortedDict(), SortedDict(), SortedDict()
    rex1 = re.compile(r"^(?:[^\\]+\\){2}([^\\]+)\\")


    # --> User interface.
    gui = interface(Interface())

    # --> Parse arguments.
    arguments = parser.parse_args(gui.arguments)


    #     ------------------------
    #  1. Inventaire des fichiers.
    #     ------------------------
    for fil in shared.filesinfolder(*arguments.extensions, folder=normpath(arguments.directory), excluded=["recycle", "\$recycle"]):
        art = None
        ext = splitext(fil)[1][1:].upper()
        ext_list.append(ext)
        match = rex1.match(normpath(fil))
        if match:
            reflist.append((fil, int(os.path.getctime(fil)), "Créé le %s" % (shared.dateformat(datetime.fromtimestamp(os.path.getctime(fil), tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1),), len(fil)))
            art = match.group(1)
        if art:
            art_list.append(art)
        if all([art, ext]):
            if art not in artext_dict:
                artext_dict[art] = list()
            artext_dict[art].append(ext)


    #     --------------------
    #  2. Total par extension.
    #     --------------------
    ext_count = collections.Counter(ext_list)

    #  Tri par nom croissant.
    ext_count1 = collections.OrderedDict(sorted(ext_count.items(), key=itemgetter(0)))

    #  Tri par total décroissant et par nom croissant.
    ext_count2 = collections.OrderedDict(sorted(sorted(ext_count.items(), key=itemgetter(0)), key=itemgetter(1), reverse=True))


    #     ------------------
    #  3. Total par artiste.
    #     ------------------
    art_count = collections.Counter(art_list)

    #  Tri par nom croissant.
    art_count1 = collections.OrderedDict(sorted(art_count.items(), key=itemgetter(0)))

    #  Tri par total décroissant et par nom croissant.
    art_count2 = collections.OrderedDict(sorted(sorted(art_count.items(), key=itemgetter(0)), key=itemgetter(1), reverse=True))


    #     -----------------------------------
    #  4. Total par couple artiste/extension.
    #     -----------------------------------
    for artist in artext_dict:
        artext_dict[artist] = collections.OrderedDict(sorted(collections.Counter(artext_dict[artist]).items(), key=itemgetter(0)))


    #     ------
    #  4. Files.
    #     ------
    if reflist:

        # ----- Liste des fichiers. Tri par nom croissant.
        lista = ((a, b, c) for a, (b, c) in enumerate([(itemgetter(0)(item), itemgetter(2)(item)) for item in sorted(reflist, key=itemgetter(0))], 1))

        # ----- Liste des 50 fichiers créés dernièrement. Tri par date décroissante, puis nom croissant.
        listb = ((a, b, c) for a, (b, c) in enumerate([(itemgetter(0)(item), itemgetter(2)(item)) for item in sorted(sorted(reflist, key=itemgetter(0)), key=itemgetter(1), reverse=True)[:50]], 1))


    #     -----------
    #  5. Extensions.
    #     -----------
    if extensions:
        listc = ((a, b, c) for a, (b, c) in enumerate([(itemgetter(0)(item), itemgetter(1)(item)) for item in sorted(extensions.items(), key=itemgetter(0))], 1))


    #     --------
    #  6. Artists.
    #     --------
    if artists:

        # ----- Liste des artistes. Tri par nom croissant.
        listd = ((a, b, c) for a, (b, c) in enumerate([(itemgetter(0)(item), itemgetter(1)(item)) for item in sorted(artists.items(), key=itemgetter(0))], 1))

        # ----- Liste des artistes. Tri par ranking décroissant, puis nom croissant.
        liste = ((a, b, c) for a, (b, c) in enumerate([(itemgetter(0)(item), itemgetter(1)(item)) for item in sorted(sorted(artists.items(), key=itemgetter(0)), key=itemgetter(1), reverse=True)], 1))


    #     -----------
    #  7. XML Output.
    #     -----------
    root = ElementTree.Element("Data", attrib=dict(css="firstcss.css"))
    se = ElementTree.SubElement(root, "Updated")
    se.text = shared.now()
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
        ElementTree.ElementTree(root).write(os.path.join(os.path.expandvars("%_COMPUTING%"), "DigitalAudioFilesList.xml"), encoding="UTF-8", xml_declaration=True)


    #     ---------------
    #  8. Ranking Output.
    #     ---------------
    if any([ext_count1, ext_count2, art_count1, art_count2, artext_dict]):
        with open(OUTFILE, mode=shared.WRITE, encoding=shared.UTF8) as fp:
            json.dump([shared.now(), ext_count1, ext_count2, art_count1, art_count2, artext_dict], fp, indent=4, ensure_ascii=False)
