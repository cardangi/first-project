# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from jinja2 import Environment, FileSystemLoader
from itertools import repeat
from subprocess import run
import sys
import os
import re


# =================
# Relative imports.
# =================
from . import shared


# ==========
# Constants.
# ==========
HEADER, TITLES, TABSIZE = "import video files", ["Set source directory.", "Set destination directory.", "Set extensions.", "Set mode.", "Copy files."], 10


# ================
# Initializations.
# ================
titles = dict(zip([str(i) for i in range(1, len(TITLES) + 1)], TITLES))


# ====================
# Regular expressions.
# ====================
regex1 = re.compile(r"^(?:\w+,\B )*(?:\w+)$")
regex2 = re.compile(r"^[\"\']([^\"\']+)[\"\']$")


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


# ========
# Classes.
# ========
class Header:
    pass


# ==========
# Functions.
# ==========
def pprint(t=None):
    run("CLS", shell=True)
    if t:
        print(t)


# ===============
# Main algorithm.
# ===============
header = Header()
header.main = HEADER
mode, copy, status = shared.WRITE, False, 100
while True:

    step, source, destination, extensions, test, list_extensions = 0, "", "", "", "Y", []

    #     ---------------------
    #  1. Set source directory.
    #     ---------------------
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header)
    while True:
        pprint(t=tmpl)
        source = input("{0}\tPlease enter source directory: ".format("".join(list(repeat("\n", 4)))).expandtabs(TABSIZE))
        if source:
            match = regex2.match(source)
            if match:
                source = match.group(1)
            if not os.path.exists(source):
                tmpl = template.render(header=header, message=list(('"{0}" is not a valid source directory.'.format(source),)))
                continue
            if not os.path.isdir(source):
                tmpl = template.render(header=header, message=list(('"{0}" is not a valid source directory.'.format(source),)))
                continue
            break

    #     --------------------------
    #  2. Set destination directory.
    #     --------------------------
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header)
    while True:
        pprint(t=tmpl)
        destination = input("{0}\tPlease enter destination directory: ".format("".join(list(repeat("\n", 4)))).expandtabs(TABSIZE))
        if destination:
            match = regex2.match(destination)
            if match:
                destination = match.group(1)
            if not os.path.exists(destination):
                tmpl = template.render(header=header, message=list(('"{0}" is not a valid destination directory.'.format(destination),)))
                continue
            if not os.path.isdir(destination):
                tmpl = template.render(header=header, message=list(('"{0}" is not a valid destination directory.'.format(destination),)))
                continue
            break

    #     ---------------
    #  3. Set extensions.
    #     ---------------
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header)
    while True:
        pprint(t=tmpl)
        extensions = input("{0}\tPlease enter extensions [eg: ext1, ext2, ext3]: ".format("".join(list(repeat("\n", 4)))).expandtabs(TABSIZE))
        if extensions:
            if not regex1.match(extensions):
                tmpl = template.render(header=header, message=list(("Extensions don\'t match the expected pattern.",)))
                continue
            break
    if extensions:
        list_extensions = extensions.split(", ")

    #     --------------
    #  4. Set test mode.
    #     --------------
    step += 1
    header.step = step
    header.title = titles[str(step)]
    tmpl = template.render(header=header)
    while True:
        pprint(t=tmpl)
        test = input("{0}\tWould you like use test mode [Y/N]? ".format("".join(list(repeat("\n", 4)))).expandtabs(TABSIZE))
        if test.upper() in shared.ACCEPTEDANSWERS:
            break

    #     ----------------
    #  5. Grab files list.
    #     ----------------
    list_files = list(enumerate(sorted([file for file in shared.filesinfolder(*list_extensions, folder=source)]), start=1))

    #     -------------------
    #  6. Display files list.
    #     -------------------
    step += 1
    header.step = step
    header.title = titles[str(step)]
    if not list_files and not copy:
        tmpl = template.render(header=header, message=list(("No files found.",)))
        code = "03"
    elif not list_files and copy:
        tmpl = template.render(header=header, message=list(("No files found.",)))
        code = "02"
    elif list_files:
        tmpl = template.render(header=header, menu=list_files, message=list(("{0} Files found.".format(len(list_files)),)))
        code = "01"

    #     ---------------
    #  7. Browse choices.
    #     ---------------
    while True:

        if code == "01":
            while True:
                pprint(t=tmpl)
                choice = input("{0}\tWould you like to copy files [Y/N]? ".format("".join(list(repeat("\n", 4)))).expandtabs(TABSIZE))
                if choice.upper() in shared.ACCEPTEDANSWERS:
                    break
            if choice.upper() == "Y":
                output = "{0};{1};{2}".format(source, destination, test.upper())
                if list_extensions:
                    output = "{0};{1}".format(output, ";".join(list_extensions))
                output = "{0}\n".format(output)
                with open(os.path.join(os.path.expandvars("%TEMP%"), "arguments"), mode=mode, encoding=shared.DFTENCODING) as fw:
                    fw.write(output)
                copy = True
                code = "02"
            elif choice.upper() == "N":
                code = "03"

        elif code == "02":
            while True:
                pprint(t=tmpl)
                choice = input("{0}\tWould you like to run copy [Y/N]? ".format("".join(list(repeat("\n", 4)))).expandtabs(TABSIZE))
                if choice.upper() in shared.ACCEPTEDANSWERS:
                    break
            if choice.upper() == "Y":
                status = 0
                break
            elif choice.upper() == "N":
                code = "03"

        elif code == "03":
            while True:
                pprint(t=tmpl)
                choice = input("{0}\tWould you like to exit program [Y/N]? ".format("".join(list(repeat("\n", 4)))).expandtabs(TABSIZE))
                if choice.upper() in shared.ACCEPTEDANSWERS:
                    break
            if choice.upper() == "Y":
                status = 99
                break
            elif choice.upper() == "N":
                mode = shared.APPEND
                break

    #     -------------
    #  8. Exit program.
    #     -------------
    if status in [0, 99]:
        break


# =============
# Exit program.
# =============
sys.exit(status)
