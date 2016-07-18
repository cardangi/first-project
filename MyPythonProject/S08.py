# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from jinja2 import Environment, PackageLoader
from os.path import expandvars, exists, join
from datetime import datetime
from string import Template
from pytz import timezone
import operator
import locale
import re


# =================
# Relative imports.
# =================
from Applications import shared


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Constants.
# ==========
DFTTEMPLATE = "$let/$art/$fil"
ALTTEMPLATE1 = "$let/$art/$alb/$fil"
ALTTEMPLATE2 = "$let/$art/$alb/$ext/$fil"
# -----
RIPPEDTRACKS = r"G:\Documents\RippedTracks.txt"
# -----
CWD = "music"
HOST = "192.168.1.20"
USER = "xavier"
PASSWORD = "14Berc10"
TIMEOUT = 60


# ========
# Classes.
# ========
class ServerConfig:
    pass


class Header:
    pass


# =============
# Declarations.
# =============
t, files, regex = Template(DFTTEMPLATE), [],\
                  re.compile(r"^(?:[^\\]+\\)(?:([a-z])\\)(?:(\1[^\\]+)\\)(?:\d\\)?(?:((\d{4})[^\\]+)\\)(?:\d\\)?(?:cd\d\\)?(?:([01])\.(?:[^\\]+\\))(\d\.\4\d{4}\.\d\.\5\d(?:(?:\.D[1-5])(?:\.T(?:0[1-9]|[1-5][0-9]))?)?"
                             r"\.([^\\.]+))$", re.IGNORECASE)


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
environment = Environment(loader=PackageLoader("Applications.CDRipper", "Templates"), trim_blocks=True, keep_trailing_newline=True)
environment.filters["fillchar"] = fillchar
environment.filters["splitstring"] = splitstring
environment.filters["ljustify"] = ljustify
environment.filters["rjustify"] = rjustify
template = environment.get_template("Sync")


# ===============
# Main algorithm.
# ===============

# Constitution de la liste des fichiers à uploader.
with open(RIPPEDTRACKS, encoding=shared.DFTENCODING) as fr:
    for fil in fr:
        if exists(fil.splitlines()[0].split(";")[2]):
            match = regex.match(fil.splitlines()[0].split(";")[2])
            if match:
                files.append((match.group(0), t.substitute(let=match.group(1), art=match.group(2), alb=match.group(3), ext=match.group(7).upper(), fil=match.group(6))))

# Constitution du script python.
if files:
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
        fw.write(template.render(configuration=config, files=sorted(files, key=operator.itemgetter(0)), header=header))
