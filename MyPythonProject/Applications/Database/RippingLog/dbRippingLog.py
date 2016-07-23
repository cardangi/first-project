# -*- coding: ISO-8859-1 -*-
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
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


def displayvalues(*t):
    l = []
    if len(t) >= 7:
        l.append("Ripped\t: {v[0]} - {0}".format(shared.dateformat(timezone("UTC").localize(datetime.utcfromtimestamp(t[0])).astimezone(timezone(shared.DFTTIMEZONE)), shared.TEMPLATE3), v=t).expandtabs(10))
        l.append("Artistsort: {v[1]}".format(v=t))
        l.append("Albumsort\t: {v[2]}".format(v=t).expandtabs(10))
        l.append("Artist\t: {v[3]}".format(v=t).expandtabs(10))
        l.append("Year\t: {v[4]}".format(v=t).expandtabs(10))
        l.append("Album\t: {v[5]}".format(v=t).expandtabs(10))
        l.append("Genre\t: {v[6]}".format(v=t).expandtabs(10))
    return l


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
regex5 = re.compile("\d+")


# ==========
# Constants.
# ==========
HEADER, TITLES, GENRES, OUTPUT, TABSIZE = "update rippinglog table", \
                                          ["Record unique ID.", "Set ripped datetime.", "Set artistsort.", "Set albumsort.", "Set artist.", "Set year.", "Set album.", "Set genre.", "Update record."], \
                                          ["Rock", "Hard Rock", "Heavy Metal", "Trash Metal", "Alternative Rock", "Black Metal", "Progressive Rock"], \
                                          os.path.join(os.path.expandvars("%TEMP%"), "arguments.json"), \
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
    number, epoch, albumsort, year, genre = "", "", "", "", ""

    #     -------------------
    #  1. Grab actual values.
    #     -------------------
    while True:
        pprint(t=tmpl)
        number = input("{0}\tPlease enter record unique ID: ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
        if number:
            if not regex5.match(number):
                tmpl = template.render(header=header, message=list(("Record unique ID must be numeric.",)))
                continue
            number = int(number)
            if not number:
                tmpl = template.render(header=header, message=list(('Record unique ID must be greater than 0.'.format(number),)))
                continue
            conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            if not conn.cursor().execute("SELECT count(*) FROM rippinglog WHERE id=?", (number,)).fetchone()[0]:
                tmpl = template.render(header=header, message=list(('No record with "{0}" as unique ID.'.format(number),)))
                continue
            for row in conn.cursor().execute("SELECT ripped, artistsort, albumsort, artist, year, album, genre, upc FROM rippinglog WHERE id=?", (number,)):
                actualepoch = int(timezone(shared.DFTTIMEZONE).localize(row["ripped"]).timestamp())
                actualripped = shared.dateformat(timezone(shared.DFTTIMEZONE).localize(row["ripped"]), shared.TEMPLATE3)
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
            tmpl = template.render(header=header, message=displayvalues(actualepoch, actualartistsort, actualalbumsort, actualartist, actualyear, actualalbum, actualgenre))
            break
        tmpl = template.render(header=header)

    #     ----------------
    #  2. Update datetime.
    #     ----------------
    while True:
        pprint(t=tmpl)
        epoch = input("{0}\tPlease enter ripped datetime new value: ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
        if epoch:
            if not regex4.match(epoch):
                tmpl = template.render(header=header, message=list(('Ripped datetime new value must be 10 digits long.',)))
                continue
            epoch = int(epoch)
            if epoch != actualepoch:
                keys.append("ripped")
                values.append(int(epoch))
                change = True
            break
        epoch = actualepoch
        break
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header, message=displayvalues(epoch, actualartistsort, actualalbumsort, actualartist, actualyear, actualalbum, actualgenre))

    #     ------------------
    #  3. Update artistsort.
    #     ------------------
    while True:
        pprint(t=tmpl)
        artistsort = input("{0}\tPlease enter artistsort new value: ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
        if artistsort:
            if artistsort != actualartistsort:
                keys.append("artistsort")
                values.append(artistsort)
                change = True
            break
        artistsort = actualartistsort
        break
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header, message=displayvalues(epoch, artistsort, actualalbumsort, actualartist, actualyear, actualalbum, actualgenre))

    #     -----------------
    #  4. Update albumsort.
    #     -----------------
    while True:
        pprint(t=tmpl)
        albumsort = input("{0}\tPlease enter albumsort new value: ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
        if albumsort:
            if not regex1.match(albumsort):
                tmpl = template.render(header=header, message=list(('Albumsort new value doesn\'t respect the expected pattern.',)))
                continue
            if albumsort != actualalbumsort:
                keys.append("albumsort")
                values.append(albumsort)
                change = True
            break
        albumsort = actualalbumsort
        break
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header, message=displayvalues(epoch, artistsort, albumsort, actualartist, actualyear, actualalbum, actualgenre))

    #     --------------
    #  5. Update artist.
    #     --------------
    while True:
        pprint(t=tmpl)
        artist = input("{0}\tPlease enter artist new value: ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
        if artist:
            if artist != actualartist:
                keys.append("artist")
                values.append(artist)
                change = True
            break
        artist = actualartist
        break
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header, message=displayvalues(epoch, artistsort, albumsort, artist, actualyear, actualalbum, actualgenre))

    #     ------------
    #  6. Update year.
    #     ------------
    while True:
        pprint(t=tmpl)
        year = input("{0}\tPlease enter year new value: ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
        if year:
            if not regex2.match(year):
                tmpl = template.render(header=header, message=list(('Year new value doesn\'t respect the expected pattern.',)))
                continue
            year = int(year)
            if year != actualyear:
                keys.append("year")
                values.append(year)
                change = True
            break
        year = actualyear
        break
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header, message=displayvalues(epoch, artistsort, albumsort, artist, year, actualalbum, actualgenre))

    #     -------------
    #  7. Update album.
    #     -------------
    while True:
        pprint(t=tmpl)
        album = input("{0}\tPlease enter album new value: ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
        if album:
            if album != actualalbum:
                keys.append("album")
                values.append(album)
                change = True
            break
        album = actualalbum
        break
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header, message=displayvalues(epoch, artistsort, albumsort, artist, year, album, actualgenre))

    #     -------------
    #  8. Update genre.
    #     -------------
    while True:
        pprint(t=tmpl)
        genre = input("{0}\tPlease enter genre new value: ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
        if genre:
            if genre not in GENRES:
                tmpl = template.render(header=header, message=list(('"{0}" is not allowed as genre.',)))
                continue
            if genre != actualgenre:
                keys.append("genre")
                values.append(genre)
                change = True
            break
        genre = actualgenre
        break
    step += 1
    header.step = step
    header.title = titles[str(step)]

    #     --------------------------------
    #  9. Have some changes been detected?
    #     --------------------------------
    code = 99
    header.title = "Exit program."
    message = displayvalues(epoch, artistsort, albumsort, artist, year, album, genre)
    message.append("\nNo changes detected.")
    tmpl = template.render(header=header, message=message)
    if change:
        code = 1
        header.title = "Export update arguments."
        tmpl = template.render(header=header, message=displayvalues(epoch, artistsort, albumsort, artist, year, album, genre))

    #     ---------------
    # 10. Browse choices.
    #     ---------------
    while True:

        #   i. Export update arguments to output file.
        if code == 1:
            while True:
                pprint(t=tmpl)
                choice = input("{0}\tWould you like to export update arguments [Y/N]? ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
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
                pprint(t=tmpl)
                choice = input("{0}\tWould you like to update database [Y/N]? ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
                if choice.upper() in shared.ACCEPTEDANSWERS:
                    break
            if choice.upper() == "Y":
                with open(OUTPUT, mode=shared.WRITE, encoding=shared.DFTENCODING) as fw:
                    json.dump(args, fw, indent=4, sort_keys=True)
                status = 0
                break
            if choice.upper() == "N":
                break

        # iii. Exit algorithm.
        elif code == 99:
            while True:
                pprint(t=tmpl)
                choice = input("{0}\tWould you like to exit program [Y/N]? ".expandtabs(TABSIZE).format("".join(list(repeat("\n", 4)))))
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
