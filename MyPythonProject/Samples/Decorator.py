# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


def f3(f):
    """
    Cette fonction est créée spécifiquement pour décorer la fonction f1.
    """
    def noname(*psargs):
        o = f(*psargs)
        return "{a}\n{b}\n{a}\n".format(a="="*len(o), b=o)
    return noname


@f3  # f1 = f3(f1)
def f1(*psargs):
    """
    Cette fonction ne peut pas être modifiée c'est pourquoi elle est décorée.
    """
    return " ".join(psargs)


print(f1("le", "petit", "bonhomme", "en", "mousse."))

# -----

# -*- coding: ISO-8859-1 -*-
# Ce script utilise quatre décorateurs.
# En revanche la syntaxe "@décorateur" n'est pas utilisée car une fois qu'une fonction est décorée elle ne peut plus être utilisée
# sans le(s) décorateur(s) !
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import re
import locale
import os.path
import argparse
from pytz import timezone
from datetime import datetime
from operator import itemgetter
from os.path import normpath, splitext
from jinja2 import Environment, PackageLoader
from sortedcontainers import SortedDict, SortedList


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
class Data:
    pass


class Header:
    pass


# ==========
# Functions.
# ==========
def prependnum(f1):
    """
    Décorer la fonction "writeheader" par insertion d'un numéro de titre.
    """
    def noname(num, stri):
        return "#. {a}. {b}".format(a=num, b=f1(stri))
    return noname


def prependchar(f2):
    """
    Décorer la fonction "writeheader" par insertion de caractères de démarquation.
    """
    def noname(num, stri, char="="):
        return "#! {a}\n{b}\n#! {a}\n".format(a=char*(len(stri)+3), b=f2(num, stri))
    return noname


def prependcrlf(f3):
    """
    Décorer la fonction "writeheader" par insertion des caractères "saut de ligne" et "retour chariot".
    """
    def noname(num, stri, crlf=3):
        return "{a}{b}".format(a="\n"*crlf, b=f3(num, stri))
    return noname


def prependcomm(f4):
    """
    Insérer une magic value en début de fichier.
    """
    def noname(num, stri):
        return "#! xavier's customized text file !\n{}".format(f4(num, stri, crlf=2))
    return noname


def writeheader(s):
    """
    Fonction reçevant une chaîne de caractères et retournant
    cette même chaîne formatée en caractères majuscules.
    """
    return s.upper()


def writeline(*tu):
    return "{} : {} fichier(s).\n".format(tu[0], tu[1])


def canfilebeprocessed(fe, *tu):
    """
    fe: file extension.
    tu: filtered extensions tuple.
    """
    if not tu:
        return True
    if tu:
        if fe.lower() in tu:
            return True
    return False


def directory(d):
    if not os.path.isdir(d):
        raise argparse.ArgumentTypeError('"{}" is not a valid directory'.format(d))
    if not os.access(d, os.R_OK):
        raise argparse.ArgumentTypeError('"{}" is not a readable directory'.format(d))
    return d


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


def hasattribute(object, name):
    if hasattr(object, name):
        return True
    return False


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dir", dest="directory", help="directory to walk through", type=directory)
parser.add_argument("-e", "--ext", dest="extension", help="one or more extension(s) to filter out", nargs="*")
parser.add_argument("outfile", help="outfile", type=argparse.FileType("wt", encoding="ISO-8859-1"))
arguments = parser.parse_args()


# ==========
# Constants.
# ==========
LAJUST = 5


# =============
# Declarations.
# =============

# Décoration totale de la fonction "writeheader".
writefirstheader = prependcomm(prependcrlf(prependchar(prependnum(writeheader))))

# Décoration partielle de la fonction "writeheader".
writeheader = prependcrlf(prependchar(prependnum(writeheader)))

# Variables.
reflist, templist, lista, listb, listd, liste, extensions, artists, t, rex1, rex2, acount, ecount = [], [], None, None, None, None, SortedDict(), SortedDict(), (), re.compile(r"^(?:[^\\]+\\){2}([^\\]+)\\"),\
                                                                                                    re.compile("recycle", re.IGNORECASE), 0, 0

# Traitement des arguments.
if arguments.extension:
    t = tuple(arguments.extension)


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=PackageLoader("Applications.CDRipper", "Templates"), trim_blocks=True, keep_trailing_newline=True, extensions=["jinja2.ext.do"])
environment.filters["fillchar"] = fillchar
environment.filters["splitstring"] = splitstring
environment.filters["ljustify"] = ljustify
environment.filters["rjustify"] = rjustify
environment.filters["hasattribute"] = hasattribute
template = environment.get_template("DigitalAudioFilesList")


# ===============
# Main algorithm.
# ===============
header, data = Header(), Data()
# -----
header.coding = shared.CODING
header.author = '__author__ = "%s"' % (shared.AUTHOR,)
header.today = shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1)
# -----
for fil in shared.directorytree(normpath(arguments.directory)):
    match = rex2.search(fil)
    if not match:
        art = None
        ext = None
        if canfilebeprocessed(splitext(fil)[1][1:], *t):
            ext = splitext(fil)[1][1:].upper()
            match = rex1.match(normpath(fil))
            if match:
                reflist.append((fil, int(os.path.getctime(fil)), "Créé le %s" % (shared.dateformat(datetime.fromtimestamp(os.path.getctime(fil), tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1),), len(fil)))
                art = match.group(1)
        if ext:
            if ext not in extensions:
                extensions[ext] = 0
            extensions[ext] += 1
            ecount += 1
        if art:
            if art not in artists:
                artists[art] = 0
            artists[art] += 1
            acount += 1


#    ------
# 1. Files.
#    ------
if reflist:

    size = max([i[3] for i in reflist]) + LAJUST

    # ----- Liste des fichiers. Tri par nom croissant.
    i = 0
    templist.clear()
    for fil, dummy1, humantime, dummy2 in SortedList(reflist):
        i += 1
        templist.append(("{0:>5}. {1:.<{2}}".format(i, fil, size), humantime))
    lista = SortedList(templist)

    # ----- Liste des 50 fichiers créés dernièrement. Tri par date décroissante, puis nom croissant.
    i = 0
    templist.clear()
    for fil, dummy1, humantime, dummy2 in sorted(SortedList(reflist), key=itemgetter(1), reverse=True)[:50]:
        i += 1
        templist.append(("{0:>5}. {1:.<{2}}".format(i, fil, size), humantime))
    listb = SortedList(templist)


#    -----------
# 2. Extensions.
#    -----------
i = 0
templist.clear()
for extension in extensions.keys():
    i += 1
    templist.append(("{0:>5}. {1:.<5}".format(i, extension.upper()), "{0:>5}".format(extensions[extension])))
listc = SortedList(templist)


#    --------
# 3. Artists.
#    --------
if artists:

    size = max([len(artist) for artist in artists.keys()])

    # ----- Liste des artistes. Tri par nom croissant.
    i = 0
    templist.clear()
    for artist in artists.keys():
        i += 1
        templist.append(("{0:>5}. {1:.<{2}}".format(i, artist, size+1), "{0:>5}".format(artists[artist])))
    listd = SortedList(templist)

    # ----- Liste des artistes. Tri par cumul décroissant, puis nom croissant.
    i = 0
    templist.clear()
    for artist, count in sorted(sorted(listd, key=itemgetter(0)), key=itemgetter(1), reverse=True):
        i += 1
        templist.append(("{0:>5}. {1}".format(i, artist[7:]), count))
    liste = SortedList(templist)


#    -------
# 4. Output.
#    -------
data.allfiles = lista
data.last50files = listb
data.extensions = listc
data.artist1 = listd
data.artist2 = liste
data.ecount = ecount
data.acount = acount
arguments.outfile.write(template.render(header=header, data=data))
