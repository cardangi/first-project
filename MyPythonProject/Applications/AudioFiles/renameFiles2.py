# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from jinja2 import Environment, FileSystemLoader
from itertools import repeat
from datetime import datetime
from string import Template
from subprocess import run
from pytz import timezone
import argparse
import logging
import sys
import os
import re


# =================
# Relative imports.
# =================
from .. import shared


# ==========
# Functions.
# ==========
def validdirectory(d):
    if not os.path.exists(d):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist'.format(d))
    if not os.path.isdir(d):
        raise argparse.ArgumentTypeError('"{0}" is not a directory'.format(d))
    return d


def pprint(t=None):
    run("CLS", shell=True)
    if t:
        print(t)


# ==========
# Arguments.
# ==========
parser = argparse.ArgumentParser()
parser.add_argument("directory", help="root directory", type=validdirectory)
parser.add_argument("--extensions", nargs="*")


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ==========
# Constants.
# ==========
HEADER, TITLES, EXTENSIONS, EXIT, MODES, TABSIZE = "rename  audio  files", \
                                                   ["Check files.", "Exit program."], \
                                                   {"flac": 13, "mp3": 1, "m4a": 2}, \
                                                   {"N": shared.BACK, "Y": shared.EXIT}, \
                                                   {"rename": "renamed", "import": "imported"}, \
                                                   10


# ====================
# Regular expressions.
# ====================
regex1 = re.compile(r"\b({0})\b\\\b({1})\.({2})\b".format(shared.DFTYEARREGEX, shared.DFTMONTHREGEX, shared.DFTDAYREGEX))
regex2 = re.compile(r"\\\bCD([1234])\b\\")
regex3 = re.compile(r".\Bd\d_(\d{2})\B")


# ========
# Classes.
# ========
class Result:
    pass


class Header:
    pass


# ================
# Initializations.
# ================
step, status, successes, fails, choice, extension_list, newname_list, arguments = 2, 0, 0, 0, "", "", [], parser.parse_args()
results = Result()
results.display = False
results.mode = "renaming"
results.successes = 0
results.fails = 0
results.files = 0


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
environment.filters["rjustify"] = shared.rjustify
environment.filters["ljustify"] = shared.ljustify


# ===================
# Jinja2 template(s).
# ===================
template = environment.get_template("T1")


# ==================
# Local template(s).
# ==================
ltmpl = Template('os.rename(src="$src", dst="$dst")')


# ==============
# Log arguments.
# ==============
logger.info("{0} {1} {0}".format("="*50, shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1)))
logger.info('START "%s".' % (os.path.basename(__file__),))
logger.debug("Directory.")
logger.debug('   "%s".' % (arguments.directory,))
if arguments.extensions:
    logger.debug("Extensions.")
    for extension in arguments.extensions:
        logger.debug("   %s." % (extension.upper(),))


# ===============
# Main algorithm.
# ===============
header = Header()
header.main = HEADER
titles = dict(zip([str(i) for i in range(3, 5)], TITLES))


#     ---------------
#  1. Grab arguments.
#     ---------------
information = ('Directory   : "{0}".'.format(arguments.directory),)
if arguments.extensions:
    for extension in arguments.extensions:
        extension_list = "{0}, {1}".format(extension_list, extension.upper())
if extension_list:
    information += ("Extensions: {0}.".format(extension_list[2:]),)
else:
    information += ("Extensions: no selected extensions.",)


#     ----------
#  2. Get files.
#     ----------
match = regex1.search(arguments.directory)
if match:
    part1 = "{0}{1}{2}".format(match.group(1), match.group(2), match.group(3))
    for file in shared.filesinfolder(extensions=arguments.extensions, folder=arguments.directory):
        disc, track = "", ""
        match2 = regex2.search(file)
        match3 = regex3.search(file)
        extension = os.path.splitext(file)[1][1:].lower()
        if match2:
            disc = match2.group(1)
        if match3:
            track = match3.group(1)
        if disc and track:
            newname_list.append((file, os.path.join(os.path.dirname(file), "2.{0}.1.{4}.D{1}.T{2}.{3}".format(part1, disc, track.zfill(2), extension, EXTENSIONS[extension]))))


#     ------------
#  3. Files found.
#     ------------
if newname_list:
    newname_list = sorted(newname_list, key=lambda i: i[0])


#     ---------------
#  4. No files found.
#     ---------------
if not newname_list:
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header, message=list(("No files found.",)))
    while True:
        pprint(tmpl)
        choice = input("{0}\tWould you like to exit program [Y/N]? ".format("".join(list(repeat("\n", 4)))).expandtabs(TABSIZE))
        if choice.upper() in shared.ACCEPTEDANSWERS:
            break
    logger.info('END "%s".' % (os.path.basename(__file__),))
    pprint()
    sys.exit(EXIT[choice.upper()])


#     --------------------
#  5. Display found files.
#     --------------------
step += 1
header.step = step
header.title = titles[str(step)]
tmpl = template.render(header=header, message=list(information), detail=newname_list, mode=MODES["rename"])
while True:
    pprint(tmpl)
    choice = input("{0}\tWould you like to rename files [Y/N]? ".format("".join(list(repeat("\n", 4)))).expandtabs(TABSIZE))
    if choice.upper() in shared.ACCEPTEDANSWERS:
        break


#     -------------
#  6. Rename files.
#     -------------
if choice.upper() == "Y":
    results.display = True
    for src, dst in newname_list:
        try:
            os.rename(src=src, dst=dst)
        except OSError:
            logger.debug('An issue occurred while renaming "%s".' % (src,))
            results.files += 1
            results.fails += 1
            status = 1
        else:
            logger.debug("Rename file.")
            logger.debug('   Source ("%s").' % (src,))
            logger.debug('   Destination ("%s").' % (dst,))
            results.files += 1
            results.successes += 1


#     ----------------
#  7. Display results.
#     ----------------
step += 1
header.step = step
header.title = titles[str(step)]
tmpl = template.render(header=header, message=list(information), results=results)
while True:
    pprint(tmpl)
    choice = input("{0}\tWould you like to exit program [Y/N]? ".format("".join(list(repeat("\n", 4)))) .expandtabs(TABSIZE))
    if choice.upper() in shared.ACCEPTEDANSWERS:
        break


#     -------------
#  8. Exit program.
#     -------------
logger.info('END "%s".' % (os.path.basename(__file__),))
pprint()
sys.exit(EXIT[choice.upper()])
