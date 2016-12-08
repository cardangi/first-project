# -*- coding: utf-8 -*-
import os
import argparse
from . import shared

__author__ = 'Xavier ROSSET'


#     =========
#  1. PARSER 1.
#     =========
zipfile = argparse.ArgumentParser()
zipfile.add_argument("source", type=shared.validpath)
zipfile.add_argument("destination", choices=["documents", "backup", "temp", "onedrive"], action=shared.GetPath)
subparsers = zipfile.add_subparsers()

# Singled extensions.
parser1_s = subparsers.add_parser("singled")
parser1_s.add_argument("extensions", nargs="+")

# Grouped extensions.
parser1_g = subparsers.add_parser("grouped")
parser1_g.add_argument("group", nargs="+", choices=["documents", "computing"], action=shared.GetExtensions)
group = parser1_g.add_mutually_exclusive_group()
group.add_argument("-e", "--excl", dest="exclude", nargs="*", action=shared.ExcludeExtensions, help="exclude enumerated extension(s)")
group.add_argument("-k", "--keep", nargs="*", action=shared.KeepExtensions, help="exclude all extensions but enumerated extension(s)")
parser1_g.add_argument("-i", "--incl", dest="include", nargs="*", action=shared.IncludeExtensions, help="include enumerated extension(s)")


#     =========
#  2. PARSER 2.
#     =========
epochconverter = argparse.ArgumentParser()
epochconverter.add_argument("start", help="Start epoch", type=shared.validepoch)
epochconverter.add_argument("end", help="End epoch", type=shared.validepoch, nargs="?", action=shared.SetEndEpoch)
epochconverter.add_argument("-z", "--zone", help="Time zone", default=shared.DFTTIMEZONE)


#     =========
#  3. PARSER 3.
#     =========
deleterippinglog = argparse.ArgumentParser()
deleterippinglog.add_argument("-d", "--db", dest="database", default=os.path.join(os.path.expandvars("%_COMPUTING%"), "database.db"), type=shared.validdb)
subparsers = deleterippinglog.add_subparsers()

# Singled record(s) unique ID.
parser3_s = subparsers.add_parser("singled")
parser3_s.add_argument("uid", nargs="+", type=int)

# Ranged records unique ID.
parser3_g = subparsers.add_parser("ranged")
parser3_g.add_argument("start", type=int)
parser3_g.add_argument("end", nargs="?", default="9999", type=int, action=shared.SetUID)


#     =========
#  4. PARSER 4.
#     =========
foldercontent = argparse.ArgumentParser()
foldercontent.add_argument("folder")
foldercontent.add_argument("extensions", nargs="*", action=shared.SetExtensions)
