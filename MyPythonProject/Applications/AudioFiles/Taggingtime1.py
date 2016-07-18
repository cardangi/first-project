# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from jinja2 import Environment, FileSystemLoader
from itertools import repeat
import subprocess
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
HEADER, TITLES, EXIT, TABSIZE = "timestamp audio files", \
                                ["Set number of files.", "Set output file.", "Create output file."], \
                                {"N": shared.BACK, "Y": shared.EXIT}, \
                                10


# ================
# Initializations.
# ================
step, number, output, answer = 0, 0, "", ""


# ====================
# Regular expressions.
# ====================
regex1 = re.compile(r"^\d(\d{1,2})?$")
regex2 = re.compile(r"^(?=.{4,}$)(?=[a-z].+$)\w+$", re.IGNORECASE)


# ==========
# Functions.
# ==========
def pprint(t=None):
    subprocess.run("CLS", shell=True)
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
environment.filters["sortedlist"] = shared.sortedlist
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
titles = dict(zip([str(i) for i in range(1, 4)], TITLES))


#     --------------------
#  1. Set number of files.
#     --------------------
step += 1
header.step = step
header.title = titles[str(step)]
tmpl = template.render(header=header)
while True:
    pprint(tmpl)
    number = input("{0}\tPlease enter number of files: ".format("".join(list(repeat("\n", 3)))).expandtabs(TABSIZE))
    if number:
        if not regex1.match(number):
            tmpl = template.render(header=header, message=list(('"{0}" is not a valid number.'.format(number),)))
            continue
        number = int(number)
        if not number:
            tmpl = template.render(header=header, message=list(('"0" is not a valid number.',)))
            continue
        break
    tmpl = template.render(header=header)


#     ----------------
#  2. Set output file.
#     ----------------
step += 1
header.step = step
header.title = titles[str(step)]
tmpl = template.render(header=header, message=list(("Number of files: {0}.".format(number),)))
while True:
    pprint(t=tmpl)
    output = input("{0}\tPlease enter output file: ".format("".join(list(repeat("\n", 3)))).expandtabs(TABSIZE))
    if output:
        if not regex2.match(output):
            tmpl = template.render(header=HEADER, step=step, title=titles[str(step)], message=list(('"{0}" is not a valid output file.'.format(output),)))
            continue
        break
    tmpl = template.render(header=header, message=list(("Number of files: {0}.".format(number),)))


#     -------------------
#  3. Create output file.
#     -------------------
step += 1
header.step = step
header.title = titles[str(step)]
while True:
    pprint(template.render(header=header, message=list(("Number of files\t: {0}.".format(number).expandtabs(), 'Output file\t: "{0}.txt".'.format(output).expandtabs()))))
    answer = input("{0}\tWould you like to create output file [Y/N]? ".format("".join(list(repeat("\n", 3)))).expandtabs(TABSIZE))
    if answer.upper() not in shared.ACCEPTEDANSWERS:
        continue
    break
if answer.upper() == "Y":
    process = subprocess.run(["python", "-m", "Applications.AudioFiles.Taggingtime2", "{0}".format(number)], stdout=subprocess.PIPE, universal_newlines=True)
    if process.returncode == 0:
        with open(os.path.join(os.path.expandvars("%TEMP%"), "{0}.txt".format(output)), mode=shared.WRITE, encoding=shared.DFTENCODING) as fw:
            fw.write(process.stdout)
        tmpl = template.render(header=header,
                               message=list(("Number of files\t: {0}.".format(number).expandtabs(),
                                             'Output file\t: "{0}.txt".'.format(output).expandtabs(),
                                             '\n\t"{0}" was created with success. You can import it to MP3Tag.'.format(os.path.join(os.path.expandvars("%TEMP%"), "{0}.txt".format(output))).expandtabs(TABSIZE)
                                             ))
                               )
    else:
        tmpl = template.render(header=header,
                               message=list(("Number of files\t: {0}.".format(number).expandtabs(),
                                             'Output file\t: "{0}.txt".'.format(output).expandtabs(),
                                             '\n\tAn issue occurred with python script "Taggingtime2.py". "{0}" can\'t be created.'.format(os.path.join(os.path.expandvars("%TEMP%"), "{0}.txt".format(output))).expandtabs(TABSIZE)
                                             ))
                               )
    pprint(tmpl)


#     -------------
#  4. Exit program.
#     -------------
while True:
    answer = input("{0}\tWould you like to exit program [Y/N]? ".format("".join(list(repeat("\n", 3)))).expandtabs(TABSIZE))
    if answer.upper() in shared.ACCEPTEDANSWERS:
        break
pprint()
sys.exit(EXIT[answer.upper()])
