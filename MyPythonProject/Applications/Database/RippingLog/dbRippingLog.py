# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# ===================
# Absolute import(s).
# ===================
from subprocess import run
from pytz import timezone
import sqlite3
import locale
import json
import sys
import os
import re


# =================
# Relative imports.
# =================
from ... import shared


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Functions.
# ==========
def pprint(t=None):
    run("CLS", shell=True)
    if t:
        print(t)


# ========
# Classes.
# ========
class Header:
    pass


# ====================
# Regular expressions.
# ====================
regex1 = re.compile("^(?=[\d\.]+$)(?=.\.[^\.]+\..$)(?=\d\.\d{8}\.\d$).\.(?:19[6-9]|20[01])\d{5}\..$")
regex2 = re.compile("^(?=\d{4}$)(?:19[6-9]|20[01])\d$")
regex3 = re.compile("^\d{12,13}$")
regex4 = re.compile("^\d{10}$")


# ==========
# Constants.
# ==========
HEADER, TITLES, GENRES, OUTPUT, TABSIZE = "convert unix epoch", \
                                          ["Set start epoch.", "Set end epoch.", "Set time zone.", "Confirm arguments"], \
                                          ["Rock", "Hard Rock", "Heavy Metal", "Trash Metal", "Alternative Rock", "Black Metal", "Progressive Rock"], \
                                          os.path.join(os.path.expandvars("%TEMP%"), "arguments"), \
                                          10


# ==================
# Initializations 1.
# ==================
args, status, code, step, number, update = [], 100, 1, 0, 0, False


# ==================
# Initializations 2.
# ==================
header = Header()
step += 1


# ===============
# Main algorithm.
# ===============
while True:

    keys, values, change = [], [], False

    #     -------------------
    #  1. Grab actual values.
    #     -------------------
    while True:
        pprint()
        number = input("Please enter record number: ")
        if number:
            conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            if not conn.cursor().execute("SELECT count(*) FROM rippinglog WHERE id=?", (number,)).fetchone()[0]:
                # tmpl = template.render(header=header, message=list(("artist: ".format(row["artist"]), "year: ".format(row["year"]), "album: ".format(row["album"]))))
                continue
            for row in conn.cursor().execute("SELECT ripped, artistsort, albumsort, artist, year, album, genre, UPC FROM rippinglog WHERE id=?", (number,)):
                actualripped = timezone(shared.DFTTIMEZONE).localize(row["ripped"]).timestamp()
                actualartistsort = row["artistsort"]
                actualalbumsort = row["albumsort"]
                actualartist = row["artist"]
                actualyear = row["year"]
                actualalbum = row["album"]
                actualgenre = row["genre"]
                actualbarcode = row["UPC"]
            # tmpl = template.render(header=header, message=list(("artist: ".format(row["artist"]), "year: ".format(row["year"]), "album: ".format(row["album"]))))
            break
        # tmpl = template.render(header=header)
    step += 1
    # header.title = ...
    # tmpl = ...

    #     ----------------
    #  2. Update datetime.
    #     ----------------
    while True:
        pprint()
        ripped = input("Please enter ripped datetime new value: ")
        if ripped:
            if not regex4.match(ripped):
                continue
            if ripped != actualripped:
                keys.append("ripped")
                values.append(ripped)
                change = True
            break
        ripped = actualripped
        break
    step += 1

    #     ------------------
    #  3. Update artistsort.
    #     ------------------
    while True:
        pprint()
        artistsort = input("Please enter artistsort new value: ")
        if artistsort:
            if artistsort != actualartistsort:
                keys.append("artistsort")
                values.append(artistsort)
                change = True
            break
        artistsort = actualartistsort
        break
    step += 1
    # header.title = ...
    # tmpl = ...

    #     -----------------
    #  4. Update albumsort.
    #     -----------------
    while True:
        pprint()
        albumsort = input("Please enter albumsort new value: ")
        if albumsort:
            if not regex1.match(albumsort):
                # tmpl = ...
                continue
            if albumsort != actualalbumsort:
                keys.append("albumsort")
                values.append(albumsort)
                change = True
            break
        albumsort = actualalbumsort
        break

    #     --------------
    #  5. Update artist.
    #     --------------
    while True:
        pprint()
        artist = input("Please enter artist new value: ")
        if artist:
            if artist != actualartist:
                keys.append("artist")
                values.append(artist)
                change = True
            break
        artist = actualartist
        break
    step += 1
    # header.title = ...
    # tmpl = ...

    #     ------------
    #  6. Update year.
    #     ------------
    while True:
        pprint()
        year = input("Please enter year new value: ")
        if year:
            if not regex2.match(year):
                # tmpl = ...
                continue
            if int(year) != actualyear:
                keys.append("year")
                values.append(year)
                change = True
            break
        year = actualyear
        break
    step += 1
    # header.title = ...
    # tmpl = ...

    #     -------------
    #  7. Update album.
    #     -------------
    while True:
        pprint()
        album = input("Please enter album new value: ")
        if album:
            if album != actualalbum:
                keys.append("album")
                values.append(album)
                change = True
            break
        album = actualalbum
        break
    step += 1
    # header.title = ...
    # tmpl = ...

    #     -------------
    #  8. Update genre.
    #     -------------
    while True:
        pprint()
        genre = input("Please enter genre new value: ")
        if genre:
            if genre not in GENRES:
                continue
            if genre != actualgenre:
                keys.append("genre")
                values.append(genre)
                change = True
            break
        genre = actualgenre
        break
    step += 1
    # header.title = ...
    # tmpl = ...

    #     --------------------------------
    #  9. Have some changes been detected?
    #     --------------------------------
    step += 1
    code = 99
    header.title = "Exit program."
    # "No changes detected."
    # tmpl = ...
    if change:
        code = 1
        header.title = "Export update arguments."
        # tmpl = ...

    #     ---------------
    # 10. Browse choices.
    #     ---------------
    while True:

        #   i. Export update arguments to output file.
        if code == 1:
            while True:
                pprint()
                choice = input("Would you like to export update arguments [Y/N]? ")
                if choice.upper() in shared.ACCEPTEDANSWERS:
                    break
            if choice.upper() == "Y" and number:
                args.append(tuple([number, dict(zip(keys, values))]))
                code += 1
            elif choice.upper() == "N" and args:
                code += 1
            elif choice.upper() == "N" and not args:
                code = 99

        #  ii. Update database.
        elif code == 2:
            while True:
                pprint()
                choice = input("Would you like to update database [Y/N]? ")
                if choice.upper() in shared.ACCEPTEDANSWERS:
                    break
            if choice.upper() == "Y":
                with open(OUTPUT, mode=shared.WRITE, encoding=shared.DFTENCODING) as fw:
                    json.dump(args, fw)
                status = 0
                break
            if choice.upper() == "N":
                break

        # iii. Exit algorithm.
        elif code == 99:
            while True:
                pprint()
                choice = input("Would you like to exit program [Y/N]? ")
                if choice.upper() in shared.ACCEPTEDANSWERS:
                    break
            if choice.upper() == "Y":
                status = 99
                break
            if choice.upper() == "N":
                break

    #     ---------------
    # 11. Exit algorithm.
    #     ---------------
    if status in [0, 99]:
        break


# ===============
# Exit algorithm.
# ===============
sys.exit(status)
