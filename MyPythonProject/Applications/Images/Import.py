# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# ======================
# Exemple d'utilisation.
# ======================
# python "G:\Documents\MyPythonProject\Launchers\Images\ImportL.py" -s nikon dir "D:\DCIM\174NIKON"
# -s nikon . . . . . . . : désigne un masque permettant de filtrer les photos à importer.
# dir "D:\DCIM\174NIKON" : désigne le répertoire source possédant les photos à importer.


# =================
# Absolute imports.
# =================
import os
import re
import sys
import locale
import argparse
from pytz import timezone
from string import Template
from datetime import datetime
from sortedcontainers import SortedList
from os.path import expandvars, isdir, join
from jinja2 import Environment, PackageLoader


# =================
# Relative imports.
# =================
from .. import shared as s1  # Applications/shared.py
from .Modules import shared as s2  # Applications/Images/Modules/shared.py


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ========
# Classes.
# ========
class BatchRename(Template):
    delimiter = "%"


# ==========
# Functions.
# ==========
def directory(d):
    if not os.path.isdir(d):
        raise argparse.ArgumentTypeError('"{}" is not a valid directory'.format(d))
    if not os.access(d, os.R_OK):
        raise argparse.ArgumentTypeError('"{}" is not a readable directory'.format(d))
    return d


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--select")
parser.add_argument("-t", "--template", nargs="?", default="%cy%{m}_%{n}")
subparser = parser.add_subparsers(dest="input")
parser_dir = subparser.add_parser("dir")
parser_dir.add_argument("dir", type=directory)
parser_fil = subparser.add_parser("fil")
parser_fil.add_argument("fil", type=argparse.FileType(encoding=s1.Global()["latin1"]))
arguments = parser.parse_args()


# ========
# Classes.
# ========
class Header:
    pass


# ==========
# Constants.
# ==========
PATTERN = "^.+\.jpg$"
PATTERNS = {"lumix": r"^p\d{7}\.jpg$", "canon": r"^_mg_\d{4}\.jpg$", "nikon": "^dscn\d{4}\.jpg$"}
TEMPLATES = ["%cy%{m}_%{n}", "%{t}"]


# ================
# Initializations.
# ================
l1, l2, o, p, t, sequence, first, template = SortedList(), [], "", None, BatchRename(arguments.template), 0, True,\
                                             Environment(loader=PackageLoader("Applications.Images", "Templates"), trim_blocks=True, keep_trailing_newline=True).get_template("Import")


# ===============
# Main algorithm.
# ===============


#    -------------
# 1. Check inputs.
#    -------------
if arguments.template not in TEMPLATES:
    sys.exit()


#    --------------
# 2. Check pattern.
#    --------------
if arguments.select:
    pattern = PATTERNS.get(arguments.select, arguments.select)
regex = re.compile(PATTERN, re.IGNORECASE)


#    -----------------------
# 3. Store files to process.
#    -----------------------
if arguments.input == "dir":
    if isdir(arguments.dir):
        for file in os.listdir(arguments.dir):
            image = s1.Images(join(arguments.dir, file))
            if regex.match(file) and image["localtimestamp"]:
                l1.add(join(arguments.dir, file))

if arguments.input == "fil":
    for file in arguments.fil:
        image = s1.Images(file.splitlines()[0])
        if regex.match("{}.{}".format(image["basename"], image["extension"])) and image["localtimestamp"]:
            l1.add(file.splitlines()[0])


#    --------------
# 4. Process files.
#    --------------

#   Création d'une liste de tuples.
#   Chaque tuple est composé de : 1) nom du fichier, 2) répertoire de destination, 3) nom du fichier importé.
for file in l1:
    image = s1.Images(file)
    sequence = s2.getsequencenumber(image["originalyear"], sequence+1)
    l2.append((file, image["defaultlocation"], image.renameto(dirn=image["defaultlocation"], basn=t.substitute(cy=image["originalyear"], m=image["originalmonth"], n=str(sequence).zfill(5), t=image["localtimestamp"]))))

#   Constitution du script python à l'aide du templating engine "Jinja2".
if l2:
    # -----
    header = Header()
    header.coding = s1.CODING
    header.author = '__author__ = "%s"' % (s1.AUTHOR,)
    header.today = s1.dateformat(datetime.now(tz=timezone(s1.DFTTIMEZONE)), s1.TEMPLATE1)
    # -----
    with open(join(expandvars("%temp%"), s1.PYSCRIPT), s1.WRITE, encoding=s1.DFTENCODING) as fw:
        fw.write(template.render(files=SortedList(l2), header=header))
