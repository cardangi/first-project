# -*- coding: ISO-8859-1 -*-
import re
from pytz import timezone
from dateutil import parser, tz
from operator import itemgetter
from Applications import shared

__author__ = 'Xavier ROSSET'


def toto(s):

    pattern = r"^((?:{0})(?:{1})(?:{2}))\B_\B(\d{{6}})(?:\((\d)\))?\.jpg$".format(shared.DFTYEARREGEX, shared.DFTMONTHREGEX, shared.DFTDAYREGEX)
    regex = re.compile(pattern, re.IGNORECASE)
    match = regex.match(s)
    if match:
        a, b, c = match.groups()
        if c is None:
            c = 0
        elif c is not None:
            c = str(int(c) + 1)
        x, y, z = tuple(map(int, (a, b, c)))
        return s, x, y, z


if __name__ == "__main__":

    tzinfos = {"CET": tz.gettz("Europe/Paris"), "CEST": tz.gettz("Europe/Paris")}
    print([(a, timezone("Europe/Paris").localize(b).timestamp()*1000 + c) for
           a, b, c in [(itemgetter(0)(i), parser.parse("{0}{1}".format(itemgetter(1)(i), itemgetter(2)(i)), tzinfos=tzinfos), itemgetter(3)(i))
                 for i in sorted(sorted(sorted(map(toto, ["20160527_095934.jpg", r"20160304_101202(0).jpg", r"20160304_101202.jpg"]), key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1))]])
