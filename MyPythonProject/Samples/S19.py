# -*- coding: utf-8 -*-
# import os
# import json
# import xml.etree.ElementTree as ElementTree
from logging.config import dictConfig
import logging
import yaml
import os
from Applications.AudioCD.shared import AudioFilesList

__author__ = 'Xavier ROSSET'


with open(os.path.join(os.path.expandvars("%_COMPUTING%"), "logging.yml"), encoding="UTF_8") as fp:
    dictConfig(yaml.load(fp))
# logger = logging.getLogger("Applications.AudioCD")

# OUTFILE = os.path.join(os.path.expandvars("%TEMP%"), "ranking.json")
mylist = AudioFilesList("flac", "mp3", folder=r"F:\K", excluded=["recycle", "\$recycle"])

# --> XML Output.
# root = ElementTree.Element("Data", attrib=dict(css="firstcss.css"))
# se = ElementTree.SubElement(root, "Updated")
# se.text = now()
# if mylist.files1:
#     se = ElementTree.SubElement(root, "Files")
#     for item1, item2, item3 in mylist.files1:
#         file = ElementTree.SubElement(se, "File", attrib=dict(number=str(item1), created=item3))
#         file.text = item2
# if mylist.files2:
#     se = ElementTree.SubElement(root, "RecentFiles")
#     for item1, item2, item3 in mylist.files2:
#         file = ElementTree.SubElement(se, "File", attrib=dict(number=str(item1), created=item3))
#         file.text = item2
# if mylist.extensions:
#     se = ElementTree.SubElement(root, "Extensions")
#     for item1, item2, item3 in mylist.extensions:
#         file = ElementTree.SubElement(se, "Extension", attrib=dict(number=str(item1), count=str(item3)))
#         file.text = item2
# if mylist.artist1:
#     se = ElementTree.SubElement(root, "Artists")
#     for item1, item2, item3 in mylist.artist1:
#         file = ElementTree.SubElement(se, "Artist", attrib=dict(number=str(item1), count=str(item3)))
#         file.text = item2
# if mylist.artist2:
#     se = ElementTree.SubElement(root, "Ranking")
#     for item1, item2, item3 in mylist.artist2:
#         file = ElementTree.SubElement(se, "Artist", attrib=dict(number=str(item1), count=str(item3)))
#         file.text = item2
# if any([mylist.files1, mylist.files2, mylist.extensions, mylist.artist1, mylist.artist2]):
#     ElementTree.ElementTree(root).write(os.path.join(os.path.expandvars("%_COMPUTING%"), "DigitalAudioFilesList.xml"), encoding="UTF-8", xml_declaration=True)
#
# # --> Ranking Output.
# if any([mylist.ext_count1, mylist.ext_count2, mylist.art_count1, mylist.art_count2, mylist.artext_count]):
#     with open(OUTFILE, mode=WRITE, encoding=UTF8) as fp:
#         json.dump([now(), mylist.ext_count1, mylist.ext_count2, mylist.art_count1, mylist.art_count2, mylist.artext_count], fp, indent=4, ensure_ascii=False)

for k, g in mylist.grouped_reflist:
    print(k)
    x = list(g)
    print(len(x))
    for item in x:
        print(item)

for k, g in mylist.groupedby_artist:
    print(k)
    x = list(g)
    print(len(x))
    for item in x:
        print(item)

for k, g in mylist.groupedby_artist_extension:
    print(k)
    x = list(g)
    print(len(x))
    for item in x:
        print(item)
