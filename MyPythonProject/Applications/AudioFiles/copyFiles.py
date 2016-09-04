# -*- coding: ISO-8859-1 -*-
import os
import re
import sys
import locale
import itertools
from operator import itemgetter
from subprocess import run, PIPE
from collections import namedtuple
from jinja2 import Environment, FileSystemLoader
from .. import shared as s1
from .Modules import shared as s2

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Constants.
# ==========
ACCEPTEDEXTENSIONS, TEMP, XXCOPYLOG, OUTFILE, TABSIZE = ["flac", "mp3", "m4a", "ogg"], \
                                                        os.path.expandvars("%TEMP%"), \
                                                        os.path.expandvars("%_XXCOPYLOG%"), \
                                                        "xxcopy", \
                                                        10


# ==========
# Functions.
# ==========
def pprint(t):
    run("CLS", shell=True)
    print(t)


def getextensions(art, path=s1.MUSIC):
    d, regex = {}, re.compile(r"\b{0}\b".format(art), re.IGNORECASE)
    for a, b, c in os.walk(path):
        if c:
            if regex.search(a):
                for fil in c:
                    ext = os.path.splitext(fil)[1][1:].lower()
                    if ext in ACCEPTEDEXTENSIONS:
                        d[ext] = d.get(ext, 0) + 1
    return d


def getfolders(art, ext, path=s1.MUSIC):
    rex1 = re.compile(r"\b{0}\b".format(art), re.IGNORECASE)
    rex2 = re.compile(r".{0}$".format(ext), re.IGNORECASE)
    for a, b, c in os.walk(path):
        if rex1.search(a):
            for fld in set([os.path.normpath(a) for fil in c if rex2.search(fil)]):
                yield(fld)


def getdrives():
    process = run("WMIC LOGICALDISK GET CAPTION", stdout=PIPE, universal_newlines=True)
    if process.returncode == 0:
        for drive in process.stdout.splitlines():
            yield drive.strip()


# ====================
# Regular expressions.
# ====================
regex1 = re.compile(r"^[a-z ]+$", re.IGNORECASE)
regex2 = re.compile(r"^[A-Z]:$")


# ======================
# Jinja2 environment(s).
# ======================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_pythonproject%"), "Applications", "AudioFiles", "Templates"), encoding=s1.DFTENCODING),
                          trim_blocks=True,
                          lstrip_blocks=True)


# ==========================
# Jinja2 global variable(s).
# ==========================
environment.globals["now"] = s1.now()
environment.globals["copyright"] = s1.COPYRIGHT


# ========================
# Jinja2 custom filter(s).
# ========================
environment.filters["integertostring"] = s1.integertostring
environment.filters["repeatelement"] = s1.repeatelement
environment.filters["sortedlist"] = s1.sortedlist
environment.filters["ljustify"] = s1.ljustify
environment.filters["rjustify"] = s1.rjustify


# ===================
# Jinja2 template(s).
# ===================
template1 = environment.get_template("T1")
template2 = environment.get_template("XXCOPY")


# ==================
# Initializations 1.
# ==================
mode, status, code, tmpl, choice = s1.WRITE, 100, 1, None, None
artist, extension, folder, command, list_indivfiles, list_files, list_drives, somesfilestocopy = "", "", "", "", [], [], [], False


# ==================
# Initializations 2.
# ==================
nt = namedtuple("nt", "maintitle step title")


# ===============
# Main algorithm.
# ===============
while True:

    #     -----------
    #  1. Set artist.
    #     -----------
    #     Then grab available extensions.
    if code == 1:
        header = s1.Header("copy  audio  files", ["Set artist.", "Set extension.", "Set folder.", "Set files."])
        head = header()
        tmpl = template1.render(header=nt(*head))
        while True:
            pprint(t=tmpl)
            artist = input("{0}\tPlease enter artist: ".format("".join(list(itertools.repeat("\n", 4)))).expandtabs(TABSIZE))
            if artist:
                if regex1.match(artist):
                    break
                tmpl = template1.render(header=nt(*head), message=list(('"{0}" is not a valid input.'.format(artist),)))
                continue
            tmpl = template1.render(header=nt(*head))
            continue
        list_extensions = list(enumerate([key.upper() for key in sorted(getextensions(artist).keys())], start=1))
        head = header()
        code = 99
        tmpl = template1.render(header=nt(*head), message=list(('No audio files found for "{0}".'.format(artist),)))
        if list_extensions:
            code = 2
            tmpl = template1.render(header=nt(*head), menu=list_extensions)

    #     --------------
    #  2. Set extension.
    #     --------------
    #     Then grab available folders.
    elif code == 2:
        while True:
            pprint(t=tmpl)
            try:
                choice = int(input("{0}\tPlease choose extension: ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE)))
            except ValueError:
                continue
            else:
                if choice > len(list_extensions):
                    continue
                break
        extension = list_extensions[choice-1][1]
        list_folders = list(enumerate(list(getfolders(artist, extension)), start=1))
        code += 1
        tmpl = template1.render(header=nt(*header()), menu=list_folders)

    #     -----------
    #  3. Set folder.
    #     -----------
    #     Then grab available files.
    elif code == 3:
        while True:
            pprint(t=tmpl)
            try:
                choice = int(input("{0}\tPlease choose folder: ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE)))
            except ValueError:
                continue
            else:
                if choice > len(list_folders):
                    continue
                break
        folder = list_folders[choice-1][1]
        list_parents = list_folders[choice-1][1].split("\\")
        list_files = list(enumerate(list(s1.filesinfolder(list((extension,)), folder)), start=1))
        code += 1
        tmpl = template1.render(header=nt(*header()), menu=list_files)

    #     ----------
    #  4. Set files.
    #     ----------
    #     Then grab available destination drives.
    elif code == 4:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\tWould you like to select individual files [Y/N]? ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            if choice.upper() in s1.ACCEPTEDANSWERS:
                break
        list_drives = list(enumerate([drive for drive in getdrives() if regex2.match(drive)], start=1))

        #  4a. Global.
        if choice.upper() == "N":
            header = s1.Header("copy  audio  files", ["Set destination drive.", "Copy files.", "Run copy command(s).", "Exit program."], 5)
            mode_files = "G"
            head = header()
            tmpl = template1.render(header=nt(*head), message=list(("An issue was encountered while grabbing available destination drives.",)))
            code = 99
            if list_drives:
                tmpl = template1.render(header=nt(*head), menu=list_drives)
                code = 6

    #  4a. Individual.
        elif choice.upper() == "Y":
            header = s1.Header("copy  audio  files", ["Set individual files.", "Set destination drive.", "Copy files.", "Run copy command(s).", "Exit program."], 5)
            mode_files = "I"
            head = header()
            tmpl = template1.render(header=nt(*head), menu=list_files)
            code += 1

    #     ---------------------
    #  5. Set individual files.
    #     ---------------------
    #     Then grab available destination drives.
    elif code == 5:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\tPlease enter file index [e.g. 1, 2, 5-7, 10]: ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            if choice:
                list_indivfiles = [itemgetter(1)(fil) for fil in list_files if itemgetter(0)(fil) in map(int, s2.formatindexes(choice))]
                if list_indivfiles:
                    break
                tmpl = template1.render(header=nt(*head), menu=list_files, message=list(("No correct indexes selected.",)))
                continue
        list_indivfiles = list(enumerate(sorted(list_indivfiles), start=1))
        head = header()
        code = 99
        tmpl = template1.render(header=nt(*head), message=list(("An issue was encountered while grabbing available destination drives.",)))
        if list_drives:
            code = 6
            tmpl = template1.render(header=nt(*head), menu=list_drives)

    #     ----------------------
    #  6. Set destination drive.
    #     ----------------------
    #     Then write copy command to temporary working file.
    elif code == 6:
        while True:
            pprint(t=tmpl)
            try:
                choice = int(input("{0}\tPlease choose destination drive: ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE)))
            except ValueError:
                continue
            else:
                if choice > len(list_drives):
                    continue
                break
        directory = "{0}{1}".format(os.path.normpath(os.path.join("{0}{1}".format(list_drives[choice-1][1], os.path.sep), list_parents[1], list_parents[2])), os.path.sep)
        if mode_files == "G":
            command = list(enumerate(list((template2.render(src=os.path.normpath("{0}{1}*.{2}".format(folder, os.path.sep, extension.lower())),
                                                            dst=directory,
                                                            dir=TEMP,
                                                            lst="xxcopy.lst",
                                                            log=XXCOPYLOG),)),
                                     start=1
                                     )
                           )
        elif mode_files == "I":
            command = list(enumerate(sorted([template2.render(src=fil,
                                                              dst=directory,
                                                              dir=TEMP,
                                                              lst="xxcopy.lst",
                                                              log=XXCOPYLOG) for num, fil in list_indivfiles]),
                                     start=1
                                     )
                           )
        code += 1
        tmpl = template1.render(header=nt(*header()), menu=command)

    #     ---------------------------------------------
    #  7. Write copy command to temporary working file.
    #     ---------------------------------------------
    #     Then run copy command(s).
    elif code == 7:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\tWould you like to copy files using the command(s) above [Y/N]? ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            if choice.upper() in s1.ACCEPTEDANSWERS:
                break
        code += 1
        if choice.upper() == "Y":
            with open(os.path.join(TEMP, OUTFILE), mode=mode, encoding=s1.DFTENCODING) as fw:
                for num, cmd in command:
                    fw.write("{0}\n".format(cmd))
            somesfilestocopy = True
            mode = s1.APPEND
            tmpl = template1.render(header=nt(*header()))
        elif choice.upper() == "N" and somesfilestocopy:
            tmpl = template1.render(header=nt(*header()))
        elif choice.upper() == "N" and not somesfilestocopy:
            header = s1.Header("copy  audio  files", ["Exit program."], 8)
            head = header()
            tmpl = template1.render(header=nt(*head))
            code = 99

    #     -----------------
    #  8. Run copy command.
    #     -----------------
    elif code == 8:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\tWould you like to run copy command(s) [Y/N]? ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            if choice.upper() in s1.ACCEPTEDANSWERS:
                break
        if choice.upper() == "Y":
            status = 0
            break
        elif choice.upper() == "N":
            code = 99
            tmpl = template1.render(header=nt(*header()))

    #     -------------
    #  9. Exit program.
    #     -------------
    elif code == 99:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\tWould you like to exit program [Y/N]? ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            if choice.upper() in s1.ACCEPTEDANSWERS:
                break
        if choice.upper() == "Y":
            status = 99
            break
        elif choice.upper() == "N":
            code = 1


# =============
# Exit program.
# =============
sys.exit(status)
