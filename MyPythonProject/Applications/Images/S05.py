# -*- coding: ISO-8859-1 -*-
import re
from pytz import timezone
from dateutil import parser, tz
from operator import itemgetter
from Applications import shared

__author__ = 'Xavier ROSSET'


pattern = r"^((?:{0})(?:{1}))(?:{2})\B_\B\d{{6}}(?:\(\d\))?\.jpg$".format(shared.DFTYEARREGEX, shared.DFTMONTHREGEX, shared.DFTDAYREGEX)


class OriginalMonth(object):

    def __init__(self, pattern):
        self._regex = None
        self.regex = pattern

    @property
    def regex(self):
        return self._regex

    @regex.setter
    def regex(self, arg):
        self._regex = re.compile(arg, re.IGNORECASE)

    def __call__(self, s):
        match = self.regex.match(s)
        if match
            return s, match.group(1)
        return None, None


class ImageData(object):

    def __init__(self, pattern):
        self._regex = None
        self.regex = pattern

    @property
    def regex(self):
        return self._regex

    @regex.setter
    def regex(self, arg):
        self._regex = re.compile(arg, re.IGNORECASE)

    def __call__(self, s):
        match = self.regex.match(s)
        if match
            a, b, c = re.split(r"\D", s)[:3]
            if not c:
                c = "0"
            else:
                c = str(int(c) + 1)
            a, b, c = tuple(map(int, (a, b, c)))
            return timezone("Europe/Paris").localize(parser.parse("{0}{1}".format(a, b))).timestamp()*1000 + c
        return None


if __name__ == "__main__":

	reflist = [(fil, month) in map(OriginalMonth(pattern), list(shared.filesinfolder(["jpg"], folder=src))) if fil]

    # tzinfos = {"CET": tz.gettz("Europe/Paris"), "CEST": tz.gettz("Europe/Paris")}
    # print([(a, timezone("Europe/Paris").localize(b).timestamp()*1000 + c) for
           # a, b, c in [(itemgetter(0)(i), parser.parse("{0}{1}".format(itemgetter(1)(i), itemgetter(2)(i)), tzinfos=tzinfos), itemgetter(3)(i))
                 # for i in sorted(sorted(sorted(map(GetImageData(pattern), ["20160527_095934.jpg", r"20160304_101202(0).jpg", r"20160304_101202.jpg"]), key=itemgetter(3)), key=itemgetter(2)), key=itemgetter(1)) if itemgetter(0)]])
