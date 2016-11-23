# -*- coding: utf-8 -*-
import argparse
from contextlib import suppress

__author__ = 'Xavier ROSSET'


# ========
# Classes.
# ========
class FooAction(argparse.Action):

    def __init__(self, option_strings, dest, **kwargs):
        super(FooAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        d = {}
        with suppress(AttributeError):
            d = getattr(namespace, "args")
        d[self.dest] = values
        setattr(namespace, "args", d)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="table")

# ----- Table "ALBUMS".
parser_updatalb = subparsers.add_parser("albums")
parser_updatalb.add_argument("uid", type=int, nargs="+")
parser_updatalb.add_argument("--artist", help="Artist", action=FooAction)
parser_updatalb.add_argument("--year", help="Year", type=int, action=FooAction)
parser_updatalb.add_argument("--album", help="Album title", action=FooAction)
parser_updatalb.add_argument("--genre", help="Genre", action=FooAction)
parser_updatalb.add_argument("--discs", help="Discs number", type=int, action=FooAction)

# ----- Table "TRACKS".
parser_updattck = subparsers.add_parser("tracks")
parser_updattck.add_argument("uid", type=int, nargs="+")
parser_updattck.add_argument("--title", help="Title", action=FooAction)

# ----- Table "DISCS".
parser_updatdsc = subparsers.add_parser("discs")
parser_updatdsc.add_argument("uid", type=int, nargs="+")
parser_updatdsc.add_argument("--field", help="Define here the field to update", action=FooAction)


# ===============
# Main algorithm.
# ===============
arguments = parser.parse_args(["albums", "1", "2", "3", "4", "--album", "toto", "--year", "1987", "--genre", "Hard Rock", "--discs", "2"])
print(arguments.uid)
print(arguments.args)
