# -*- coding: ISO-8859-1 -*-
from jinja2 import Environment, FileSystemLoader
from itertools import repeat
from subprocess import run
from pytz import timezone
import sqlite3
import locale
import json
import sys
import os
import re
from ... import shared

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ======================
# Jinja2 environment(s).
# ======================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "AudioFiles", "Templates"), encoding=shared.DFTENCODING), trim_blocks=True, lstrip_blocks=True)


# ==========================
# Jinja2 global variable(s).
# ==========================
environment.globals["now"] = shared.now()
environment.globals["copyright"] = shared.COPYRIGHT


# ========================
# Jinja2 custom filter(s).
# ========================
environment.filters["integertostring"] = shared.integertostring
environment.filters["repeatelement"] = shared.repeatelement
environment.filters["sortedlist"] = shared.sortedlist
environment.filters["ljustify"] = shared.ljustify
environment.filters["rjustify"] = shared.rjustify


# ===================
# Jinja2 template(s).
# ===================
template = environment.get_template("T1")


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
HEADER, TITLES, GENRES, OUTPUT, TABSIZE = "update rippinglog table", \
                                          ["Record number.", "Set end epoch.", "Set time zone.", "Confirm arguments"], \
                                          ["Rock", "Hard Rock", "Heavy Metal", "Trash Metal", "Alternative Rock", "Black Metal", "Progressive Rock"], \
                                          os.path.join(os.path.expandvars("%TEMP%"), "arguments"), \
                                          10


# ==================
# Initializations 1.
# ==================
args, status, number, update, titles = [], 100, 0, False, dict(zip([str(i) for i in range(1, len(TITLES) + 1)], TITLES))


# ==================
# Initializations 2.
# ==================
step = 1
header = Header()
header.main = HEADER
header.step = step
header.title = titles[str(step)]
tmpl = template.render(header=header)
code = 1


# ===============
# Main algorithm.
# ===============
while True:

    keys, values, change = [], [], False

    #     -------------------
    #  1. Grab actual values.
    #     -------------------
    while True:
        pprint(t=tmpl)
        number = input("{0}\tPlease enter record number: ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
        if number:
            if not re.compile("\d+").match(number):
                tmpl = template.render(header=header, message=list(("Record unique ID must be numeric!",)))
                continue
            uid = int(number)
            if not(uid):
                continue
            conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            if not conn.cursor().execute("SELECT count(*) FROM rippinglog WHERE id=?", (uid,)).fetchone()[0]:
                tmpl = template.render(header=header, message=list(('No record with "{0}" as unique ID.'.format(uid),)))
                continue
            for row in conn.cursor().execute("SELECT ripped, artistsort, albumsort, artist, year, album, genre, UPC FROM rippinglog WHERE id=?", (uid,)):
                actualripped = timezone(shared.DFTTIMEZONE).localize(row["ripped"]).timestamp()
                actualartistsort = row["artistsort"]
                actualalbumsort = row["albumsort"]
                actualartist = row["artist"]
                actualyear = row["year"]
                actualalbum = row["album"]
                actualgenre = row["genre"]
                actualbarcode = row["UPC"]
            step += 1
            header.step = step
            header.title = titles[str(step)]
            tmpl = template.render(header=header, message=list(("artist: {0}".format(actualartist), "year: {0}".format(actualyear), "album: {0}".format(actualalbum))))
            break
        tmpl = template.render(header=header)

    #     ----------------
    #  2. Update datetime.
    #     ----------------
    while True:
        pprint(t=tmpl)
        ripped = input("{0}\tPlease enter ripped datetime new value: ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
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
