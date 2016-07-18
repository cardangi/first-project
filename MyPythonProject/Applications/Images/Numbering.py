# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import sys
import glob
import locale
import argparse
from pytz import timezone
from string import Template
from datetime import datetime
from jinja2 import Environment, PackageLoader
from os.path import exists, expandvars, join, normpath


# =================
# Relative imports.
# =================
from .. import shared


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ========
# Classes.
# ========
class BatchRename(Template):
    delimiter = "%"


class Header:
    pass


# ==========
# Functions.
# ==========
def year(y):
    import re
    regex = re.compile(r"^20[01][0-9]$")
    if not regex.match(y):
        raise argparse.ArgumentTypeError('"{}" is not a valid year'.format(y))
    return y


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("year", type=year)
parser.add_argument("-t", "--template", nargs="?", default="%cy%{m}_%{n}")
parser.add_argument("-s", "--start", nargs="?", type=int, default=1)
arguments = parser.parse_args()


# ==========
# Constants.
# ==========
TEMPLATES = ["%cy%{m}_%{n}", "%{t}"]


# ================
# Initializations.
# ================
l1, l2, l3, t1, t2, template = [], [], [], BatchRename(arguments.template), Template("${newname}ren"),\
                               Environment(loader=PackageLoader("Applications.Images", "Templates"), trim_blocks=True, keep_trailing_newline=True).get_template("Numbering")


# ===============
# Main algorithm.
# ===============


# --> 1. Fin de l'algorithme si le template reçu n'est pas valide.
if arguments.template not in TEMPLATES:
    sys.exit()


# --> 2. Sélection des fichiers images.
for i in range(1, 13):
    curdir = normpath(join("h:/", "{0}{1}".format(arguments.year, str(i).zfill(2))))
    if exists(curdir):
        with shared.chgcurdir(curdir):
            for file in glob.glob("*.jpg"):
                img = shared.Images(join(curdir, file))
                if img["localtimestamp"]:
                    l1.append((join(curdir, file), img["localtimestamp"], img["originalyear"], img["originalmonth"]))


# --> 3. Tri des fichiers images par timestamp croissant.
# --> 4. Renommage des fichiers pour éviter tout doublon rejeté par l'OS. Le préfixe "ren" est ajouté.
# --> 5. Séquencage des fichiers.
if l1:

    # --
    # 3.
    # --
    lsorted = sorted(l1, key=lambda x: x[1])

    # --
    # 4.
    # --
    for tup in lsorted:
        img = shared.File(tup[0])
        l2.append((tup[0], img.renameto(basn=t2.substitute(newname=img["basename"]))))

    # --
    # 5.
    # --
    for sequence, (file, localtimestamp, originalyear, originalmonth) in enumerate(lsorted, start=arguments.start):
        img = shared.Images(file)
        l3.append((img.renameto(basn=t2.substitute(newname=img["basename"])), img.renameto(dirn=img["defaultlocation"], basn=t1.substitute(cy=originalyear, m=originalmonth, n=str(sequence).zfill(5), t=localtimestamp))))


# --> 6. Constitution du script python.
if l2 and l3:
    # -----
    header = Header()
    header.coding = shared.CODING
    header.author = '__author__ = "%s"' % (shared.AUTHOR,)
    header.today = shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1)
    # -----
    with open(join(expandvars("%temp%"), shared.PYSCRIPT), shared.WRITE, encoding=shared.DFTENCODING) as fw:
        fw.write(template.render(header=header, list1=l2, list2=l3))
