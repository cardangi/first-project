# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from jinja2 import Environment, FileSystemLoader
from itertools import repeat
from subprocess import run
import json
import sys
import os
import re


# =================
# Relative imports.
# =================
from .. import shared


# ==========
# Constants.
# ==========
HEADER, TITLES, INPUTS, OUTFILE, TABSIZE = "rename  audio  files", \
                                           ["Set directory.", "Set extensions."], \
                                           ["Please enter root directory", "Please enter extensions"], \
                                           os.path.join(os.path.expandvars("%TEMP%"), "arguments.json"), \
                                           10


# ================
# Initializations.
# ================
step, directory, extensions_list, args = 0, "", "", []


# ====================
# Regular expressions.
# ====================
regex1 = re.compile(r"^(?:\w+,\B )*(?:\w+)$")
regex2 = re.compile(r"^(?:\w+\b )*(?:\w+)$")
regex3 = re.compile(r'^"([^"]+)"$')


# ==========
# Functions.
# ==========
def directoryok(d):
    if not os.path.exists(d):
        return False
    if not os.path.isdir(d):
        return False
    return True


def pprint(t=None):
    run("CLS", shell=True)
    if t:
        print(t)


# ========
# Classes.
# ========
class Header:
    pass


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
environment.filters["ljustify"] = shared.ljustify
environment.filters["rjustify"] = shared.rjustify


# ===================
# Jinja2 template(s).
# ===================
template = environment.get_template("T1")


# ===============
# Main algorithm.
# ===============
header = Header()
header.main = HEADER
titles, inputs = dict(zip([str(i) for i in range(1, 3)], TITLES)), dict(zip([str(i) for i in range(1, 3)], INPUTS))


#     -----------------------------------
#  1. Grab directory from keyboard input.
#     -----------------------------------
step += 1
header.step = step
header.title = titles[str(step)]
tmpl = template.render(header=header)
while True:
    pprint(tmpl)
    directory = input("{0}\t{1}: ".format("".join(list(repeat("\n", 4))), inputs["1"]).expandtabs(TABSIZE))
    if directory:
        match = regex3.match(directory)
        if match:
            directory = match.group(1)
        if not directoryok(directory):
            tmpl = template.render(header=header, message=list(('"{0}" is not a valid directory!'.format(directory),)))
            continue
        break
    tmpl = template.render(header=header)


#     ------------------------------------
#  2. Grab extensions from keyboard input.
#     ------------------------------------
step += 1
header.step = step
header.title = titles[str(step)]
tmpl = template.render(header=header, message=list(('Directory: "{0}".'.format(directory),)))
while True:
    pprint(tmpl)
    extensions = input("{0}\t{1}: ".format("".join(list(repeat("\n", 4))), inputs["2"]).expandtabs(TABSIZE))
    if not extensions:
        extensions_list = []
        break
    match1 = regex1.match(extensions)
    match2 = regex2.match(extensions)
    if match1:
        extensions_list = [i.strip() for i in extensions.split(",")]
        break
    if match2:
        extensions_list = [i.strip() for i in extensions.split()]
        break
    continue
args.append(tuple([directory, extensions_list]))


#     ---------------------------
#  3. Return arguments to caller.
#     ---------------------------
with open(OUTFILE, mode=shared.WRITE, encoding=shared.DFTENCODING) as fp:
    json.dump(args, fp, indent=4)


#     -------------
#  4. Exit program.
#     -------------
sys.exit(0)
