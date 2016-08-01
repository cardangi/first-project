# -*- coding: ISO-8859-1 -*-
from jinja2 import Environment, FileSystemLoader
from string import Template
import subprocess
import itertools
import argparse
import fnmatch
import locale
import sys
import os
import re
from .. import shared as s1
from .Modules import shared as s2

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Arguments.
# ==========
parser = argparse.ArgumentParser()
parser.add_argument("extension")


# ==========
# Functions.
# ==========
def pprint(t=None):
    subprocess.run("CLS", shell=True)
    if t:
        print(t)


def directorytree(directory=os.getcwd(), rex=None):
    for root, folders, files in os.walk(directory):
        for file in files:
            if rex:
                if not rex.search(os.path.join(root, file)):
                    continue
            yield os.path.join(root, file)


# ========
# Classes.
# ========
class Header:
    pass


# ======================
# Jinja2 environment(s).
# ======================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "AudioFiles", "Templates"), encoding=s1.DFTENCODING), trim_blocks=True, lstrip_blocks=True)


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


# ================
# Local templates.
# ================
template3 = Template(r"F:\S\Springsteen, Bruce\2\$year\$month.$day - $location\CD$disc\1.Free Lossless Audio Codec")


# ==========
# Constants.
# ==========
HEADER, TITLES, MODES, INPUTS, CURWDIR, TABSIZE = "import audio files", \
                                                  ["Set current directory.", "Set source folder.", "Import files.", "Run import."], \
                                                  {"copy": "copied", "import": "imported"}, \
                                                  ["Would you like to change the current directory [Y/N]? ",
                                                   "Please choose source folder: ",
                                                   "Would you like to import files [Y/N]? ",
                                                   "Would you like to exit program [Y/N]? ",
                                                   "Would you like to run import [Y/N]? ",
                                                   "Please enter directory: ",
                                                   "Would you like to import the previous chosen files [Y/N]? ",
                                                   ], \
                                                  os.path.join(os.path.expandvars("%_MYMUSIC%"), r"Bruce Springsteen & The E Street Band"), \
                                                  10


# ================
# Initializations.
# ================
mode, status, somefilesimported, curwdir, set_folders, list_folders, list_files, srcs, dsts = s1.WRITE, 100, False, CURWDIR, set(), [], [], "", ""
titles = dict(zip([str(i) for i in range(1, len(TITLES) + 1)], TITLES))
inputs = dict(zip([str(i) for i in range(1, len(INPUTS) + 1)], INPUTS))
# -----
step = 1
header = Header()
header.main = HEADER
header.step = step
header.title = titles[str(step)]
tmpl = template1.render(header=header, message=list(('Current directory is: "{0}"'.format(CURWDIR),)))
inp, code = 1, 1
# -----
arguments = parser.parse_args()


# ====================
# Regular expressions.
# ====================
rex1 = re.compile(r"^\d(\d\d?)?$")
rex2 = re.compile(r"\b({0})\b\-\b({1})\b\-\b({2})\b \b([a-z, ]+)\\[^\\\.]+\.(?:{3})$".format(s1.DFTYEARREGEX, s1.DFTMONTHREGEX, s1.DFTDAYREGEX, arguments.extension), re.IGNORECASE)
rex3 = re.compile(r"\b({0})\b\-\b({1})\b\-\b({2})\b \b([a-z, ]+)$".format(s1.DFTYEARREGEX, s1.DFTMONTHREGEX, s1.DFTDAYREGEX), re.IGNORECASE)
rex4 = re.compile(r"[a-z]\B(?:1[1-9])(?:{0})(?:{1})d(\d)\B_".format(s1.DFTMONTHREGEX, s1.DFTDAYREGEX), re.IGNORECASE)


# ===============
# Main algorithm.
# ===============
while True:

    #     -----------------------------------------------------
    #  1. Grab available source folders from current directory.
    #     -----------------------------------------------------
    if code == 1:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\t{1} ".format("".join(list(itertools.repeat("\n", 3))), inputs[str(inp)]).expandtabs(TABSIZE))
            if choice.upper() not in s1.ACCEPTEDANSWERS:
                continue
            break
        if choice.upper() == "Y":
            tmpl = template1.render(header=header)
            while True:
                pprint(t=tmpl)
                curwdir = input("{0}\t{1} ".format("".join(list(itertools.repeat("\n", 3))), inputs["6"]).expandtabs(TABSIZE))
                if curwdir:
                    if not os.path.exists(curwdir):
                        tmpl = template1.render(header=header, message=list(('"{0}" is not a valid directory!'.format(curwdir),)))
                        continue
                    if not os.path.isdir(curwdir):
                        tmpl = template1.render(header=header, message=list(('"{0}" is not a valid directory!'.format(curwdir),)))
                        continue
                    break
                tmpl = template1.render(header=header)
        step += 1
        header.step = step
        header.title = titles[str(step)]
        set_folders = {os.path.dirname(file) for file in directorytree(directory=curwdir, rex=rex2)}
        if set_folders:
            list_folders = sorted(list(zip(range(1, len(set_folders) + 1), sorted(set_folders))), key=lambda i: i[0])
            tmpl = template1.render(header=header, menu=list_folders)
            inp, code = 2, 2
        elif not set_folders:
            tmpl = template1.render(header=header, message=list(("No folders found.",)))
            inp, code = 4, 99

    #     ----------------------------------------
    #  2. Grab available files from source folder.
    #     ----------------------------------------
    elif code == 2:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\t{1}: ".format("".join(list(itertools.repeat("\n", 3))), inputs[str(inp)]).expandtabs(TABSIZE))
            if choice:
                if not rex1.match(choice):
                    tmpl = template1.render(header=header, menu=list_folders)
                    continue
                if int(choice) > len(list_folders):
                    tmpl = template1.render(header=header, menu=list_folders)
                    continue
                break
            tmpl = template1.render(header=header, menu=list_folders)
        step += 1
        header.step = step
        header.title = titles[str(step)]
        src = list_folders[int(choice) - 1][1]
        match1 = rex3.search(src)
        if match1:
            list_files = [file for file in os.listdir(src) if fnmatch.fnmatch(file, "*.{0}".format(arguments.extension.lower()))]
            srcs = [os.path.join(src, file) for file in list_files]
            dsts = ["{0}{1}".format(template3.substitute(year=match1.group(1), month=match1.group(2), day=match1.group(3), location=match1.group(4), disc=s2.grabdiscnumber(file, rex4).number), os.path.sep)
                    for file in list_files if s2.grabdiscnumber(file, rex4).found]
            tmpl = template1.render(header=header, detail=sorted(list(zip(sorted(srcs), sorted(dsts))), key=lambda i: i[0]), mode=MODES["import"])
            inp, code = 3, 4
        elif not match1:
            tmpl = template1.render(header=header, message=list(('"{0}" doesn\'t match the expected pattern.'.format(src),)))
            inp, code = 4, 99

    #     -------------
    #  3. Import files.
    #     -------------
    elif code == 4:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\t{1} ".format("".join(list(itertools.repeat("\n", 3))), inputs[str(inp)]).expandtabs(TABSIZE))
            if choice.upper() in s1.ACCEPTEDANSWERS:
                break
        if choice.upper() == "Y":
            with open(os.path.join(os.path.expandvars("%TEMP%"), "xxcopy.txt"), mode=mode, encoding=s1.DFTENCODING) as fw:
                for src, dst in sorted(list(zip(srcs, dsts)), key=lambda i: i[0]):
                    fw.write("{0}\n".format(template2.render(src=src, dst=dst, log=os.path.expandvars("%_XXCOPYLOG%"))))
            header.title = titles["4"]
            mode, inp, code, somefilesimported = s1.APPEND, 5, 5, True
        elif choice.upper() == "N" and not somefilesimported:
            header.title = "Exit program."
            inp, code = 4, 99
        elif choice.upper() == "N" and somefilesimported:
            header.title = titles["4"]
            inp, code = 7, 5
        step += 1
        header.step = step
        tmpl = template1.render(header=header)

    #     -----------
    #  4. Run import.
    #     -----------
    elif code == 5:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\t{1} ".format("".join(list(itertools.repeat("\n", 3))), inputs[str(inp)]).expandtabs(TABSIZE))
            if choice.upper() in s1.ACCEPTEDANSWERS:
                break
        if choice.upper() == "N":
            inp, code = 4, 99
            step += 1
            header.step = step
            header.title = "Exit program."
            tmpl = template1.render(header=header)
        elif choice.upper() == "Y":
            status = 0
            break

    #     -------------
    #  5. Exit program.
    #     -------------
    elif code == 99:
        while True:
            pprint(t=tmpl)
            choice = input("{0}\t{1} ".format("".join(list(itertools.repeat("\n", 3))), inputs[str(inp)]).expandtabs(TABSIZE))
            if choice.upper() in s1.ACCEPTEDANSWERS:
                break
        if choice.upper() == "N":
            step, inp, code = 1, 1, 1
            header.step = step
            header.title = titles[str(step)]
            tmpl = template1.render(header=header, message=list(('Current directory is: "{0}"'.format(CURWDIR),)))
        elif choice.upper() == "Y":
            status = 99
            break


# =============
# Exit program.
# =============
sys.exit(status)
