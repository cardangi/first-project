# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import xml.etree.ElementTree as ElementTree
from datetime import datetime
from pytz import timezone
import sqlite3
import os
import re


# =================
# Relative imports.
# =================
from ... import shared


# ================
# Initializations.
# ================
previousart, regex1, regex2, regex3 = "", re.compile(r"[, ]"), re.compile(r"\s+"), re.compile(r"\\")


# ===============
# Main algorithm.
# ===============

# 1. Ouverture de la connexion à la base de données.
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row

# 2. Initialisation de la structure XML.
root = ElementTree.Element("Data", attrib=dict(css="digitalaudiobase.css", timestamp=shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE2)))

# 3. Itération sur les données composant les tables ALBUMS, DISCS et TRACKS.
for rowa in conn.cursor().execute("SELECT artist, year, album, albumid FROM albums ORDER BY albumid"):

    # Artist node.
    if previousart != rowa["artist"]:
        previousart = rowa["artist"]
        artist = ElementTree.SubElement(root, "Artist", attrib=dict(name=rowa["artist"]))
        artistid = ElementTree.SubElement(artist, "ArtistID")
        artistid.text = regex1.sub("", rowa["albumid"][2:-13])

    # AlbumSort node.
    albumsort = ElementTree.SubElement(artist, "AlbumSort", attrib=dict(id=rowa["albumid"][-12:]))

    # --> Album ID.
    albumid = ElementTree.SubElement(albumsort, "AlbumID")
    albumid.text = "%s%s" % (regex1.sub("", rowa["albumid"][2:-13]), rowa["albumid"][-12:].replace(".", ""))

    # --> Album year.
    year = ElementTree.SubElement(albumsort, "Year")
    year.text = str(rowa["year"])

    # --> Album title.
    album = ElementTree.SubElement(albumsort, "Album")
    album.text = rowa["album"]

    # --> Album cover.
    cover = ElementTree.SubElement(albumsort, "Cover")
    cover.text = "file:///%s" % (regex3.sub("/", regex2.sub(r"%20", os.path.join(r"C:\Users\Xavier\Documents\Album Art", rowa["albumid"][:1], rowa["albumid"][2:-13], rowa["albumid"][-12:], r"iPod-Front.jpg"))),)

    # Disc node.
    for rowd in conn.cursor().execute("SELECT discid FROM discs WHERE albumid=? ORDER BY discid", (rowa["albumid"],)):

        # --> Disc ID.
        disc = ElementTree.SubElement(albumsort, "Disc", attrib=dict(id=str(rowd["discid"])))

        # --> Tracks listing.
        for rowt in conn.cursor().execute("SELECT trackid, title FROM tracks WHERE albumid=? and discid=? ORDER BY trackid", (rowa["albumid"], rowd["discid"])):
            track = ElementTree.SubElement(disc, "Track", attrib=dict(id=str(rowt["trackid"])))
            track.text = rowt["title"]

# 4. Fermeture de la connexion à la base de données.
conn.close()

# 5. Restitution des données.
ElementTree.ElementTree(root).write(os.path.join(os.path.expandvars("%TEMP%"), "DigitalAudioBase.xml"), encoding="UTF-8", xml_declaration=True)
