# -*- coding: ISO-8859-1 -*-
from Applications import shared
from datetime import date
import itertools
import re

__author__ = 'Xavier ROSSET'


def myfunc(obj):
    return obj.index, obj.artistsort, obj.artist


# ==============
# Bootleg track.
# ==============
x = ["Springsteen, Bruce;Paris;France;2016-01-25;1;BITUSA Tour;CD;1;32;titre1", "Pearl Jam;Paris;France;2016-01-25;1;Binaural Tour;Digital;1;32;titre1"]
print("\n\n    ============")
print("1. Bootleg tracks.")
print("    ============")
tracks = list(map(shared.Bootleg, x, itertools.repeat(9)))
if all([track.iscomplete for track in tracks]):
    if all([track.aredatavalid for track in tracks]):
        for track in tracks:
            print("-----")
            for i in track:
                print(i)
            print("-----")
            print(track.index)
            print(track.tour)
            print(track.city)
            print(track.country)
            print(track.artistsort)
            print(track.artist)
            print(track.media)
            print(track.track)
            print(track.totaltracks)
            print(track.title)
            r = track.date
            if r.succeeded:
                print(r.date.year)
                print(r.date.month)
                print(r.date.day)
                d = date(*list(map(int, [r.date.year, r.date.month, r.date.day])))
                print(d)


print("---------")
print(list(map(myfunc, tracks)))
print("----------")

# A voir si cela marche...
# c.executemany("INSERT INTO albums (id, artistsort, artist) VALUES (?, ?, ?)", map(myfunc, tracks))

# ===============
# Default  track.
# ===============
x = ["Iron Maiden;1983;1;Piece of Mind;1;9;Where Eagles Dare", "Iron Maiden;1983;1;Piece of Mind;2;9;The Trooper", "Dylan, Bob;1983;1;Infidels;4;9;License to Kill"]
print("\n\n    ===========")
print("2. Default tracks.")
print("    ===========")
tracks = list(map(shared.Default, x, itertools.repeat(6)))
if all([track.iscomplete for track in tracks]):
    if all([track.aredatavalid for track in tracks]):
        for track in tracks:
            print(track.index)
            print(track.artistsort)
            print(track.artist)
            print(track.year)
            print(track.album)
            print(track.track)
            print(track.totaltracks)
            print(track.title)

x = ["springsteen, bruce", "pearl jam"]
print(list(map(re.sub, itertools.repeat(r"\W+"), itertools.repeat("."), x)))
print(list(map(re.split, itertools.repeat(r"\W+"), x)))

# with open(r"file") as fp:
#     tracks = list(shared.Bootleg.gettrackfromfile(fp=fp, fields=9))
#     if all([track.iscomplete for track in tracks]):
#         if all([track.aredatavalid for track in tracks]):
#             for track in tracks:
#                 break
