# -*- coding: utf-8 -*-
import os
import sys
import json
import sqlite3
from Applications import shared

__author__ = 'Xavier ROSSET'


# ==========
# Constants.
# ==========
OUTPUT, KEYS = os.path.join(os.path.expandvars("%TEMP%"), "rippinglog.json"), ["RIPPED", "ARTISTSORT", "ALBUMSORT", "ARTIST", "YEAR", "ALBUM", "GENRE", "BARCODE", "APPLICATION"]


# ===============
# Main algorithm.
# ===============
with open(OUTPUT, mode=shared.WRITE, encoding="UTF_8") as fp:
    conn = sqlite3.connect(shared.DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    args = []
    for row in conn.cursor().execute("SELECT rowid AS uid, ripped, artistsort, albumsort, artist, year, album, genre, upc, application FROM rippinglog ORDER BY uid DESC"):
        dict1 = dict(zip(KEYS, [shared.dateformat(shared.LOCAL.localize(row["ripped"]), shared.TEMPLATE4),
                                row["artistsort"],
                                row["albumsort"],
                                row["artist"],
                                row["year"],
                                row["album"],
                                row["genre"],
                                row["upc"],
                                row["application"]]))
        args.append(tuple([row["uid"], dict1]))
    args.insert(0, shared.now())
    json.dump(args, fp, indent=4, sort_keys=True)
    conn.close()


# ===============
# Exit algorithm.
# ===============
sys.exit(0)
