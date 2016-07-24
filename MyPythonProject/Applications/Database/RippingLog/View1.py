# -*- coding: utf-8 -*-

import os
import locale
import sqlite3
from pytz import timezone
from string import Template
from dateutil import parser
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from ... import shared

__author__ = 'Xavier ROSSET'


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Database", "RippingLog", "Templates")), trim_blocks=True, lstrip_blocks=True)


# ================
# Jinja2 template.
# ================
content = environment.get_template("Content")
t2 = environment.get_template("T2")


# ===============
# Local template.
# ===============
path = Template(r"file:///C:/Users/Xavier/Documents/Album Art/$a/$b/$c/iPod-Front.jpg")


# ===============
# Main algorithm.
# ===============


#  1. Ouverture de la connexion à la base de données.
conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row


#  2. Détail des CDs rippés.
tr4 = [tuple([shared.dateformat(timezone(shared.DFTTIMEZONE).localize(row["ripped"]), shared.TEMPLATE2),
              row["artist"],
              row["year"],
              row["album"],
              path.substitute(a=row["artistsort"][0].upper(), b=row["artistsort"], c=row["albumsort"]).replace(" ", r"%20")
              ])
       for row in conn.cursor().execute("SELECT id, ripped, artistsort, albumsort, artist, year, album FROM rippinglog ORDER BY id DESC") if row["albumsort"] and row["artistsort"]
       ]


#  3. Journal des CDs rippés. Cumul par artiste. Tri par artiste croissant.
tr1 = t2.render(id="artist1",
                h2="Palmarès par artiste",
                th=["artist", "count"],
                tr=[tuple([row["artist"], row["count"]]) for row in conn.cursor().execute("SELECT artist, count(*) AS count from rippinglog GROUP BY artist ORDER BY artist")]
                )


#  4. Journal des CDs rippés. Cumul par artiste. Tri par cumul décroissant.
tr2 = t2.render(id="artist2",
                h2="Palmarès par artiste",
                th=["artist", "count"],
                tr=[tuple([row["artist"], row["count"]])
                    for row in conn.cursor().execute("SELECT a.artist, a.count FROM (SELECT artist AS artist, count(*) AS count from rippinglog GROUP BY artist ORDER BY artist) a ORDER BY count DESC, artist")])


#  5. Journal des CDs rippés. Cumul par genre. Tri par cumul décroissant.
tr3 = t2.render(id="genre",
                h2="Palmarès par genre",
                th=["genre", "count"],
                tr=[tuple([row["genre"], row["count"]])
                    for row in conn.cursor().execute("SELECT a.genre, a.count FROM (SELECT genre AS genre, count(*) AS count from rippinglog GROUP BY genre ORDER BY genre) a ORDER BY count DESC, genre")])


#  6. Journal des CDs rippés. Cumul par période. Tri par période croissante.
#     Une date respectant le masque "SSAA MM 01" est parsée afin d'extraire le nom du mois et l'année.
tr5 = t2.render(id="month",
                h2="Palmarès par mois",
                th=["month", "count"],
                tr=[tuple(["%s %s" % (parser.parse("%s 01" % (row["ccyymm"],)).strftime("%B").capitalize(),
                                      parser.parse("%s 01" % (row["ccyymm"],)).strftime("%Y")
                                      ),
                           row["count"]
                           ])
                    for row in conn.cursor().execute("SELECT a.ccyymm AS ccyymm, count(*) AS count FROM (SELECT strftime('%Y %m', ripped) AS ccyymm FROM rippinglog) a GROUP BY a.ccyymm ORDER BY a.ccyymm")
                    ]
                )


#     -----------------------------------------------
#  8. Fermeture de la connexion à la base de données.
#     -----------------------------------------------
conn.close()


#     ------------
#  9. HTML Output.
#     ------------
print(content.render(now=shared.dateformat(shared.UTC.localize(datetime.utcnow()).astimezone(shared.LOCAL), shared.TEMPLATE4),
                     content1=tr4,
                     content2="{0}{1}{2}{3}".format(tr1, tr2, tr3, tr5)
                     )
      )
