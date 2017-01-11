# -*- coding: utf-8 -*-
import yaml
import locale
import os.path
import argparse
import datetime
from os.path import normpath
from operator import itemgetter
from Applications import shared
from logging.config import dictConfig
import xml.etree.ElementTree as ElementTree
from Applications.AudioCD.shared import AudioFilesList
from Applications.descriptors import Folder, Extensions


__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ========
# Classes.
# ========
class LocalInterface(shared.GlobalInterface):

    # Data descriptor(s).
    folder = Folder()
    extensions = Extensions()

    # Instance method(s).
    def __init__(self, *args):
        super(LocalInterface, self).__init__(*args)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="mandatory directory to walk through", type=shared.validpath)
parser.add_argument("extensions", help="one or more extension(s) to filter out", nargs="*")


# ========
# Logging.
# ========
with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # -->  1. Initializations.
    arguments = []

    # -->  2. User interface.
    gui = shared.interface(LocalInterface([("Please enter directory to walk through", "folder"), ("Please enter extension(s) to filter out", "extensions")]))

    # -->  3. Parse arguments.
    arguments.append(gui.folder)
    arguments.extend(gui.extensions)
    arguments = parser.parse_args(arguments)

    # -->  4. Create list interface.
    mylist = AudioFilesList(*arguments.extensions, folder=normpath(arguments.directory), excluded=["recycle", "\$recycle"])

    # -->  5. XML Output.
    root = ElementTree.Element("Data", attrib=dict(css="firstcss.css"))
    se = ElementTree.SubElement(root, "Updated")
    se.text = shared.now()

    #  5.a. Files list.
    if mylist.sortedby_extension:
        se = ElementTree.SubElement(root, "Files")
        for item1, item2, item3 in [(num, fil, shared.dateformat(shared.LOCAL.localize(datetime.datetime.fromtimestamp(ctime)), shared.TEMPLATE2))
                                    for num, (fil, ext, art, ctime) in enumerate(mylist.sortedby_extension, start=1)]:
            file = ElementTree.SubElement(se, "File", attrib=dict(number=str(item1), created=item3))
            file.text = item2

    #  5.b. Last fifty files list.
    if mylist.reflist:
        se = ElementTree.SubElement(root, "RecentFiles")
        for item1, item2, item3 in [(num, fil, shared.dateformat(shared.LOCAL.localize(datetime.datetime.fromtimestamp(ctime)), shared.TEMPLATE2))
                                    for num, (fil, ext, art, ctime) in enumerate(sorted(sorted(mylist.reflist, key=itemgetter(0)), key=itemgetter(3), reverse=True)[:50], start=1)]:
            file = ElementTree.SubElement(se, "File", attrib=dict(number=str(item1), created=item3))
            file.text = item2

    #  5.c. Extensions list.
    if mylist.sortedby_extension:
        se = ElementTree.SubElement(root, "Extensions")
        for item1, item2, item3 in [(num, ext.upper(), count) for num, (ext, count) in enumerate([(k, len(list(g))) for k, g in mylist.groupedby_extension], start=1)]:
            file = ElementTree.SubElement(se, "Extension", attrib=dict(number=str(item1), count=str(item3)))
            file.text = item2

    #  5.d. Artists list.
    if mylist.sortedby_artist:
        se = ElementTree.SubElement(root, "Artists")
        for item1, item2, item3 in [(num, ext, count) for num, (ext, count) in enumerate([(k, len(list(g))) for k, g in mylist.groupedby_artist], start=1)]:
            file = ElementTree.SubElement(se, "Artist", attrib=dict(number=str(item1), count=str(item3)))
            file.text = item2

    #  5.e. Extensions by artist list.
    if mylist.sortedby_artist_extension:

        # Sorted by artist in ascending order then extension in ascending order.
        se = ElementTree.SubElement(root, "Counts")
        for key, group in mylist.countby_artist_extension:
            sse = ElementTree.SubElement(se, "Artist", attrib=dict(name=key))
            for item1, item2, item3, item4 in [(num, art, ext, count) for num, (art, ext, count) in enumerate(list(group), start=1)]:
                extension = ElementTree.SubElement(sse, "Extension", attrib=dict(number=str(item1), count=str(item4)))
                extension.text = item3.upper()

        # Sorted by artist in ascending order then count in descending order.
        se = ElementTree.SubElement(root, "AlternativeCounts")
        for key, group in mylist.alternative_countby_artist_extension:
            sse = ElementTree.SubElement(se, "Artist", attrib=dict(name=key))
            for item1, item2, item3, item4 in [(num, art, ext, count) for num, (art, ext, count) in enumerate(list(group), start=1)]:
                extension = ElementTree.SubElement(sse, "Extension", attrib=dict(number=str(item1), count=str(item4)))
                extension.text = item3.upper()

    if any([mylist.reflist, mylist.reflist, mylist.sortedby_extension, mylist.sortedby_artist, mylist.sortedby_artist_extension]):
        ElementTree.ElementTree(root).write(os.path.join(os.path.expandvars("%_COMPUTING%"), "DigitalAudioFilesList.xml"), encoding="UTF-8", xml_declaration=True)
