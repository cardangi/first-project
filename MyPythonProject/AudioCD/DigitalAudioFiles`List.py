# -*- coding: utf-8 -*-
import json
import locale
import os.path
import argparse
from os.path import normpath
from Applications import shared
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


# ==========
# Constants.
# ==========
OUTFILE = os.path.join(os.path.expandvars("%TEMP%"), "ranking.json")


# ===============
# Main algorithm.
# ===============
if __name__ == "__main__":

    # -->  Initializations.
    arguments = []

    # --> User interface.
    gui = shared.interface(LocalInterface([("Please enter directory to walk through", "folder"), ("Please enter extension(s) to filter out", "extensions")]))

    # --> Parse arguments.
    arguments.append(gui.folder)
    arguments.extend(gui.extensions)
    arguments = parser.parse_args(arguments)

    # --> Create list interface.
    mylist = AudioFilesList(*arguments.extensions, folder=normpath(arguments.directory), excluded=["recycle", "\$recycle"])

    # --> XML Output.
    root = ElementTree.Element("Data", attrib=dict(css="firstcss.css"))
    se = ElementTree.SubElement(root, "Updated")
    se.text = shared.now()
    if mylist.files1:
        se = ElementTree.SubElement(root, "Files")
        for item1, item2, item3 in mylist.files1:
            file = ElementTree.SubElement(se, "File", attrib=dict(number=str(item1), created=item3))
            file.text = item2
    if mylist.files2:
        se = ElementTree.SubElement(root, "RecentFiles")
        for item1, item2, item3 in mylist.files2:
            file = ElementTree.SubElement(se, "File", attrib=dict(number=str(item1), created=item3))
            file.text = item2
    if mylist.extensions:
        se = ElementTree.SubElement(root, "Extensions")
        for item1, item2, item3 in mylist.extensions:
            file = ElementTree.SubElement(se, "Extension", attrib=dict(number=str(item1), count=str(item3)))
            file.text = item2
    if mylist.artist1:
        se = ElementTree.SubElement(root, "Artists")
        for item1, item2, item3 in mylist.artist1:
            file = ElementTree.SubElement(se, "Artist", attrib=dict(number=str(item1), count=str(item3)))
            file.text = item2
    if mylist.artist2:
        se = ElementTree.SubElement(root, "Ranking")
        for item1, item2, item3 in mylist.artist2:
            file = ElementTree.SubElement(se, "Artist", attrib=dict(number=str(item1), count=str(item3)))
            file.text = item2
    if any([mylist.files1, mylist.files2, mylist.extensions, mylist.artist1, mylist.artist2]):
        ElementTree.ElementTree(root).write(os.path.join(os.path.expandvars("%_COMPUTING%"), "DigitalAudioFilesList.xml"), encoding="UTF-8", xml_declaration=True)

    # --> Ranking Output.
    if any([mylist.ext_count1, mylist.ext_count2, mylist.art_count1, mylist.art_count2, mylist.artext_count]):
        with open(OUTFILE, mode=shared.WRITE, encoding=shared.UTF8) as fp:
            json.dump([shared.now(), arguments.directory, arguments.extensions, mylist.ext_count1, mylist.ext_count2, mylist.art_count1, mylist.art_count2, mylist.artext_count], fp, indent=4, ensure_ascii=False)
