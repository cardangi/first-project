# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import os
import re
import sys
import locale
import itertools
from subprocess import run, PIPE
from jinja2 import Environment, FileSystemLoader


# =================
# Relative imports.
# =================
from .. import shared


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Constants.
# ==========
ACCEPTEDEXTENSIONS, TEMP, XXCOPYLOG, OUTFILE, HEADER, TITLES, EXIT, TABSIZE = ["flac", "mp3", "m4a", "ogg"], \
                                                                              os.path.expandvars("%TEMP%"), \
                                                                              os.path.expandvars("%_XXCOPYLOG%"), \
                                                                              "xxcopy", \
                                                                              "copy  audio  files", \
                                                                              ["Set artist.", "Set extension.", "Set folder.", "Set files."], \
                                                                              {"N": shared.BACK, "Y": shared.EXIT}, \
                                                                              10


# ==========
# Functions.
# ==========
def pprint(t):
    run("CLS", shell=True)
    print(t)


def getextensions(art, path=shared.MUSIC):
    d, regex = {}, re.compile(r"\b{0}\b".format(art), re.IGNORECASE)
    for a, b, c in os.walk(path):
        if c:
            if regex.search(a):
                for fil in c:
                    ext = os.path.splitext(fil)[1][1:].lower()
                    if ext in ACCEPTEDEXTENSIONS:
                        if ext in d:
                            d[ext] += 1
                        else:
                            d[ext] = 1
    return d


def getfolders(art, ext, path=shared.MUSIC):
    rex1 = re.compile(r"\b{0}\b".format(art), re.IGNORECASE)
    rex2 = re.compile(r".{0}$".format(ext), re.IGNORECASE)
    for a, b, c in os.walk(path):
        if rex1.search(a):
            search = False
            for fil in c:
                if rex2.search(fil):
                    search = True
            if search:
                yield(os.path.normpath(a))


def getdrives():
    process = run("WMIC LOGICALDISK GET CAPTION", stdout=PIPE, universal_newlines=True)
    if process.returncode == 0:
        for drive in process.stdout.splitlines():
            yield drive.strip()


def getfileindex(index, lst):
    l = []
    rex1 = re.compile(r"^\d{1,2}$")
    rex2 = re.compile(r"^(\d{1,2})\-(\d{1,2})$")
    for i in index.split(", "):
        match = False
        if not match:
            match = rex1.match(i)
            if match:
                i = int(i)
                if i <= len(lst):
                    l.append(i)
        if not match:
            match = rex2.match(i)
            if match:
                if int(match.group(2)) >= int(match.group(1)):
                    for j in range(int(match.group(1)), int(match.group(2))+1):
                        if j <= len(lst):
                            l.append(j)
    return sorted(l)


# ========
# Classes.
# ========
class Header:
    pass


# ====================
# Regular expressions.
# ====================
regex1 = re.compile(r"^[a-z ]+$", re.IGNORECASE)
regex2 = re.compile(r"^[A-Z]:$")


# ======================
# Jinja2 environment(s).
# ======================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_pythonproject%"), "Applications", "AudioFiles", "Templates"), encoding=shared.DFTENCODING), trim_blocks=True, lstrip_blocks=True)


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
template1 = environment.get_template("T1")
template2 = environment.get_template("XXCOPY")


# ================
# Initializations.
# ================
titles, mode, status = dict(zip([str(i) for i in range(1, 5)], TITLES)), shared.WRITE, 100
# -----
step = 1
header = Header()
header.main = HEADER
header.step = step
header.title = titles[str(step)]
tmpl = template1.render(header=header)
code = 1
# -----
artist, extension, folder, command, indx_indivfiles, list_indivfiles, list_files, list_drives, mode_files, somesfilestocopy = "", "", "", "", [], [], [], [], "G", False


# ===============
# Main algorithm.
# ===============
while True:

    #     -----------
    #  1. Set artist.
    #     -----------
    #     Then grab available extensions.
    if code == 1:
        while True:
            pprint(t=tmpl)
            artist = input("{0}\tPlease enter artist: ".format("".join(list(itertools.repeat("\n", 4)))).expandtabs(TABSIZE))
            if artist:
                if regex1.match(artist):
                    break
                tmpl = template1.render(header=header, message=list(('"{0}" is not a valid input.'.format(artist),)))
                continue
            tmpl = template1.render(header=header)
            continue
        list_extensions = list(enumerate([key.upper() for key in sorted(getextensions(artist).keys())], start=1))
        tmpl = template1.render(header=header, message=list(('No audio files found for "{0}".'.format(artist),)))
        code = 99
        if list_extensions:
            code = 2
            step += 1
            header.step = step
            header.title = titles[str(step)]
            tmpl = template1.render(header=header, menu=list_extensions)

    #     --------------
    #  2. Set extension.
    #     --------------
    #     Then grab available folders.
    elif code == 2:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\tPlease choose extension: ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            try:
                choice = int(choice)
            except ValueError:
                continue
            else:
                if choice > len(list_extensions):
                    continue
                break
        extension = list_extensions[choice-1][1]
        list_folders = list(enumerate([folder for folder in getfolders(artist, extension)], start=1))
        code += 1
        step += 1
        header.step = step
        header.title = titles[str(step)]
        tmpl = template1.render(header=header, menu=list_folders)

    #     -----------
    #  3. Set folder.
    #     -----------
    #     Then grab available files.
    elif code == 3:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\tPlease choose folder: ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            try:
                choice = int(choice)
            except ValueError:
                continue
            else:
                if choice > len(list_folders):
                    continue
                break
        folder = list_folders[choice-1][1]
        list_parents = list_folders[choice-1][1].split("\\")
        list_files = list(enumerate([file for file in shared.filesinfolder(list((extension,)), folder)], start=1))
        code += 1
        step += 1
        header.step = step
        header.title = titles[str(step)]
        tmpl = template1.render(header=header, menu=list_files)

    #     ----------
    #  4. Set files.
    #     ----------
    #     Then grab available destination drives.
    elif code == 4:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\tWould you like to select individual files [Y/N]? ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        step += 1
        header.step = step

        #  4a. Global.
        if choice.upper() == "N":
            header.title = "Set destination drive."
            list_drives = list(enumerate([drive for drive in getdrives() if regex2.match(drive)], start=1))
            tmpl = template1.render(header=header, message=list(("An issue was encountered while grabbing available destination drives.",)))
            code = 99
            if list_drives:
                tmpl = template1.render(header=header, menu=list_drives)
                code = 6

    #  4a. Individual.
        elif choice.upper() == "Y":
            header.title = "Set individual files."
            tmpl = template1.render(header=header, menu=list_files)
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
                indfiles_index = getfileindex(index=choice, lst=list_files)
                if indfiles_index:
                    break
                tmpl = template1.render(header=header, menu=list_files, message=list(("No correct indexes selected.",)))
                continue
        mode_files = "I"
        list_indivfiles = list(enumerate([list_files[i-1][1] for i in indfiles_index], start=1))
        code = 99
        step += 1
        header.step = step
        header.title = "Set destination drive."
        list_drives = list(enumerate([drive for drive in getdrives() if regex2.match(drive)], start=1))
        tmpl = template1.render(header=header, message=list(("An issue was encountered while grabbing available destination drives.",)))
        if list_drives:
            code = 6
            tmpl = template1.render(header=header, menu=list_drives)

    #     ----------------------
    #  6. Set destination drive.
    #     ----------------------
    #     Then write copy command to temporary working file.
    elif code == 6:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\tPlease choose destination drive: ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            try:
                choice = int(choice)
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
        step += 1
        header.step = step
        header.title = "Copy files."
        tmpl = template1.render(header=header, menu=command)

    #     ---------------------------------------------
    #  7. Write copy command to temporary working file.
    #     ---------------------------------------------
    #     Then run copy command(s).
    elif code == 7:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\tWould you like to copy files using the command(s) above [Y/N]? ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        code += 1
        step += 1
        header.step = step
        if choice.upper() == "Y":
            with open(os.path.join(TEMP, OUTFILE), mode=mode, encoding=shared.DFTENCODING) as fw:
                for num, cmd in command:
                    fw.write("{0}\n".format(cmd))
            somesfilestocopy = True
            mode = shared.APPEND
            header.title = "Run copy command(s)."
            tmpl = template1.render(header=header)
        elif choice.upper() == "N" and somesfilestocopy:
            header.title = "Run copy command(s)."
            tmpl = template1.render(header=header)
        elif choice.upper() == "N" and not somesfilestocopy:
            header.title = "Exit program."
            tmpl = template1.render(header=header)
            code = 99

    #     -----------------
    #  8. Run copy command.
    #     -----------------
    elif code == 8:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\tWould you like to run copy command(s) [Y/N]? ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        if choice.upper() == "Y":
            status = 0
            break
        elif choice.upper() == "N":
            code = 99
            step += 1
            header.step = step
            header.title = "Exit program."
            tmpl = template1.render(header=header)

    #     -------------
    #  9. Exit program.
    #     -------------
    elif code == 99:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\tWould you like to exit program [Y/N]? ".format("".join(list(itertools.repeat("\n", 2)))).expandtabs(TABSIZE))
            if choice.upper() in shared.ACCEPTEDANSWERS:
                break
        if choice.upper() == "Y":
            status = 99
            break
        elif choice.upper() == "N":
            code, step = 1, 1
            header.step = step
            header.title = titles[str(step)]
            tmpl = template1.render(header=header)


# =============
# Exit program.
# =============
sys.exit(status)
