# -*- coding: utf-8 -*-
import os
import locale
import argparse
from pytz import timezone
from string import Template
from datetime import datetime
from collections import Counter
from operator import itemgetter
from Applications import shared
from jinja2 import Environment, FileSystemLoader
from Applications.Database.RippedCD.shared import select

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "AudioCD", "Templates")), trim_blocks=True, lstrip_blocks=True)


# ================
# Jinja2 template.
# ================
content = environment.get_template("Content")
t2 = environment.get_template("T2")


# ===============
# Local template.
# ===============
path = Template(r"file:///C:/Users/Xavier/Documents/Album Art/$a/$b/$c/iPod-Front.jpg")


# ==========
# Functions.
# ==========
def getfirstletter(artistsort, artist=None):
    if artistsort:
        return artistsort[0].upper()
    if artist:
        return artist[0].upper()


def validdb(arg):
    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError('"{0}" doesn\'t exist.'.format(arg))
    return arg


# ==========
# Constants.
# ==========
OUTPUT = os.path.join(os.path.expandvars("%TEMP%"), "rippedcd.html")


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=validdb)


# ===============
# Main algorithm.
# ===============
arguments = parser.parse_args()


#     -----------------------
#  1. Extraction des données.
#     -----------------------
data = list(select(arguments.database))


#     --------------------------------------------
#  2. Initialisation des variables intermédiaires.
#     --------------------------------------------
months = dict(set([(shared.dateformat(shared.LOCAL.localize(itemgetter(1)(item)), "$Y$m"),
                    shared.dateformat(shared.LOCAL.localize(itemgetter(1)(item)), "$month $Y")) for item in data]))


#     ----------------------
#  3. Détail des CDs rippés.
#     ----------------------
tr4 = [(
           shared.dateformat(shared.LOCAL.localize(itemgetter(1)(item)), shared.TEMPLATE2),
           itemgetter(2)(item),
           itemgetter(3)(item),
           itemgetter(4)(item),
           path.substitute(a=getfirstletter(itemgetter(9)(item), itemgetter(2)(item)), b=itemgetter(9)(item), c=itemgetter(8)(item)).replace(" ", r"%20")
       ) for item in data]


#     ---------------------------------------------------------------------
#  4. Journal des CDs rippés. Cumul par artiste. Tri par artiste croissant.
#     ---------------------------------------------------------------------
tr1 = t2.render(id="artist1",
                h2="Palmarès par artiste",
                th=["artist", "count"],
                tr=sorted(list(Counter([itemgetter(2)(item) for item in data]).items()), key=itemgetter(0))
                )


#     ---------------------------------------------------------------------
#  5. Journal des CDs rippés. Cumul par artiste. Tri par cumul décroissant.
#     ---------------------------------------------------------------------
tr2 = t2.render(id="artist2",
                h2="Palmarès par artiste",
                th=["artist", "count"],
                tr=sorted(sorted(list(Counter([itemgetter(2)(item) for item in data]).items()), key=itemgetter(0)), key=itemgetter(1), reverse=True)
                )


#     -------------------------------------------------------------------
#  6. Journal des CDs rippés. Cumul par genre. Tri par cumul décroissant.
#     -------------------------------------------------------------------
tr3 = t2.render(id="genre",
                h2="Palmarès par genre",
                th=["genre", "count"],
                tr=sorted(sorted(list(Counter([itemgetter(6)(item) for item in data]).items()), key=itemgetter(0)), key=itemgetter(1), reverse=True)
                )


#     ----------------------------------------------------------------------
#  7. Journal des CDs rippés. Cumul par période. Tri par période croissante.
#     ----------------------------------------------------------------------
tr5 = t2.render(id="month",
                h2="Palmarès par mois",
                th=["month", "count"],
                tr=[(months[itemgetter(0)(item)], itemgetter(1)(item))
                    for item in sorted(list(Counter([shared.dateformat(timezone(shared.DFTTIMEZONE).localize(itemgetter(1)(item)), "$Y$m") for item in data]).items()), key=itemgetter(0))]
                )


#     ------------
#  8. HTML Output.
#     ------------
with open(OUTPUT, mode=shared.WRITE, encoding=shared.UTF8) as fp:
    fp.write(content.render(now=shared.dateformat(shared.UTC.localize(datetime.utcnow()).astimezone(shared.LOCAL), shared.TEMPLATE4), 
                            content1=tr4, 
                            content2="{0}{1}{2}{3}".format(tr1, tr2, tr3, tr5)
                           )
            )
