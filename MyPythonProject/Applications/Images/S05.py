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
        if c is not None:
            c = str(int(c) + 1)
        if c is None:
            c = 0
        return tuple(map(int, (a, b, c)))


if __name__ == "__main__":

    print(sorted(sorted(sorted(map(toto, ["20160527_095934.jpg", r"20160304_101202(0).jpg", r"20160304_101202.jpg"]), key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0)))
    tzinfos = {"CET": tz.gettz("Europe/Paris"), "CEST": tz.gettz("Europe/Paris")}
    # print([timezone("Europe/Paris").localize(y).strftime("%d/%m/%Y %H:%M:%S %Z%z") for
    #        y in [parser.parse("{0}{1}".format(itemgetter(0)(i), itemgetter(1)(i)), tzinfos=tzinfos)
    #              for i in sorted(sorted(sorted(map(toto, ["20160527_095934.jpg", r"20160304_101202(0).jpg", r"20160304_101202.jpg"]), key=itemgetter(2)), key=itemgetter(1)), key=itemgetter(0))]])
    # print(toto(r"20160304_101202(1).jpg"))
    # print(toto(r"20160307_100504.jpg"))
