# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from os.path import basename, exists, expandvars, isdir, isfile, join, relpath, splitdrive, splitext
from jinja2 import Environment, PackageLoader
from sortedcontainers import SortedList
from datetime import datetime
from filecmp import dircmp
from pytz import timezone
from ftplib import FTP
import argparse
import logging
import locale
import os
import re


# =================
# Relative imports.
# =================
from .. import shared


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="subparser")
parser_1 = subparsers.add_parser("1")
parser_1.add_argument("-b", "--batch", action="store_true")
parser_2 = subparsers.add_parser("2")
parser_3 = subparsers.add_parser("3")
arguments = parser.parse_args()


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, basename(__file__)))


# ========
# Classes.
# ========
class ServerConfig:
    pass


class Header:
    pass


# ==========
# Functions.
# ==========
def left(cmpobj):

    files = []

    for item in cmpobj.left_only:
        if isfile(join(cmpobj.left, item)):
            if splitext(join(cmpobj.left, item))[1].lstrip(".").lower() == "jpg":
                files.append(join(cmpobj.left, item))

    for sub_cmpobj in cmpobj.subdirs.values():
        for item in left(sub_cmpobj):
            files.append(item)

    return files


def right(cmpobj):

    files = []

    for item in cmpobj.right_only:
        if isfile(join(cmpobj.right, item)):
            if splitext(join(cmpobj.right, item))[1].lstrip(".").lower() == "jpg":
                files.append(join(cmpobj.right, item))

    for sub_cmpobj in cmpobj.subdirs.values():
        for item in right(sub_cmpobj):
            files.append(item)

    return files


def differences(cmpobj):

    files = []

    for item in cmpobj.diff_files:
        if isfile(join(cmpobj.left, item)):
            if splitext(join(cmpobj.left, item))[1].lstrip(".").lower() == "jpg":
                files.append(join(cmpobj.left, item))

    for sub_cmpobj in cmpobj.subdirs.values():
        for item in differences(sub_cmpobj):
            files.append(item)

    return files


# ==========
# Constants.
# ==========
CWD = "pictures"
HOST = "192.168.1.20"
USER = "xavier"
PASSWORD = "14Berc10"
TIMEOUT = 60
LEFT = "h:\\"
RIGHT = r"\\diskstation\pictures"


# =============
# Declarations.
# =============
regex1, regex2, actions, folders, output, titles = re.compile(r"^20[012]\d(?:0[1-9]|1[0-2])?$"), re.compile(r"^(?=\d.+$)(?:(?:0[1-9]|1[0-2])(?:\.)?)?(?:0[1-9]|[12][0-9]|3[01])?$"),\
                                                   {}, [], False, {"00_CREATE": "Directories created.",
                                                                   "01_DELETE": "Files removed from the server.",
                                                                   "02_UPLOAD": "Files uploaded to the server."}


# ======================
# Jinja2 custom filters.
# ======================
def fillchar(length, char="-", prefix=0):
    return char*(length + prefix)


def splitstring(s, sep):
    """
    Jinja2 custom filter. Return a list of the words in the characters string 's' using 'sep' as delimiter.
    :param s: characters string.
    :param sep: delimiter.
    :return: list of the words.
    """
    return s.split(sep)


def ljustify(s, width, fillchar=""):
    """
    Jinja2 custom filter. Return the string left justified in a string of length 'width'. Padding is done using the specified character 'fillchar'.
    """
    return "{0:{2}<{1}}".format(s, width, fillchar)


def rjustify(s, width, fillchar=""):
    """
    Jinja2 custom filter. Return the string right justified in a string of length 'width'. Padding is done using the specified character 'fillchar'.
    """
    return "{0:{2}>{1}}".format(s, width, fillchar)


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=PackageLoader("Applications.Images", "Templates"), trim_blocks=True, keep_trailing_newline=True)
environment.filters["fillchar"] = fillchar
environment.filters["splitstring"] = splitstring
environment.filters["ljustify"] = ljustify
environment.filters["rjustify"] = rjustify
template = environment.get_template("Sync")


# ================
# Initializations.
# ================
actions["00_CREATE"] = []
actions["01_DELETE"] = []
actions["02_UPLOAD"] = []


# ===============
# Main algorithm.
# ===============


#     ---------
# --> PARTIE 1.
#     ---------
#     Création à droite des répertoires n'existant que dans le répertoire de gauche.
if arguments.subparser in ["1", "3"]:

    # I.1. New directory comparison object.
    cmp = dircmp(LEFT, RIGHT)

    # I.2. Inventaire des répertoires n'existant que dans le répertoire de gauche.
    for folder in cmp.left_only:
        if isdir(join(cmp.left, folder)):
            if regex1.match(folder):
                folders.append(folder)
        for a, b, c in os.walk(join(cmp.left, folder)):
            for sub_folder in b:
                if regex2.match(sub_folder):
                    folders.append(splitdrive(join(a, sub_folder))[1].lstrip("\\").replace("\\", "/"))

    # I.3. Création des répertoires énumérés à l'étape I.2.
    if folders:

        # --> Création directe.
        if (arguments.subparser == "1" and not arguments.batch) or (arguments.subparser == "3"):

            # I.3.a. Open FTP session.
            session = FTP(host=HOST, user=USER, passwd=PASSWORD, timeout=TIMEOUT)

            # I.3.b. Set current working directory.
            session.cwd(CWD)

            # I.3.c. Directory creation.
            for folder in SortedList(folders):
                logger.info('Folder "%s" created.' % folder)
                session.mkd(folder)

            # I.3.d. Close FTP session.
            session.quit()

        # --> Création différée.
        if arguments.subparser == "1" and arguments.batch:
            output = True
            actions["00_CREATE"] = SortedList(folders)


#     ---------
# --> PARTIE 2.
#     ---------
#     Synchronisation des fichiers.
#     Suppression des fichiers n'existant que dans le répertoire de droite.
#     Upload des fichiers n'existant que dans le répertoire de gauche.
#     Upload des fichiers communs présentant une différence.
#     La synchronisation est exécutée de manière différée.
if arguments.subparser in ["2", "3"]:

    # II.1. New directory comparison object.
    cmp = dircmp(LEFT, RIGHT)

    # II.2. Suppression des fichiers n'existant que dans le répertoire de droite.
    for item in right(cmp):
        output = True
        actions["01_DELETE"].append(relpath(item, start=RIGHT).replace("\\", "/"))

    # II.3. Upload des fichiers n'existant que dans le répertoire de gauche.
    for item in left(cmp):
        output = True
        actions["02_UPLOAD"].append((relpath(item, start=LEFT).replace("\\", "/"), item))

    # II.4. Upload des fichiers communs présentant une différence.
    for item in differences(cmp):
        output = True
        actions["02_UPLOAD"].append((relpath(item, start=LEFT).replace("\\", "/"), item))


#     ---------
# --> PARTIE 3.
#     ---------
if output and ((arguments.subparser == "1" and arguments.batch) or arguments.subparser in ["2", "3"]):
    # -----
    for key in sorted(actions.keys()):
        if not actions[key]:
            del actions[key]
    # -----
    config = ServerConfig()
    config.host = HOST
    config.user = USER
    config.password = PASSWORD
    config.timeout = TIMEOUT
    config.cwd = CWD
    # -----
    header = Header()
    header.coding = shared.CODING
    header.author = '__author__ = "%s"' % (shared.AUTHOR,)
    header.today = shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1)
    # -----
    with open(join(expandvars("%temp%"), shared.PYSCRIPT), mode=shared.WRITE, encoding=shared.DFTENCODING) as fw:
        fw.write(template.render(configuration=config, header=header, titles=titles, actions=actions))
