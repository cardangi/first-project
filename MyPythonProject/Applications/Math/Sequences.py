# -*- coding: ISO-8859-1 -*-
from jinja2 import Environment, FileSystemLoader
from decimal import Decimal, InvalidOperation
import subprocess
import argparse
import sys
import os
from .Modules import shared as s1
from .. import shared as s2

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def cls():
    subprocess.run("CLS", shell=True)


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("type", help="type of the sequence: arithmetic or geometric.", choices=["A", "G"])


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_pythonproject%"), "Applications", "Math", "Templates"), encoding=s2.DFTENCODING),
                          trim_blocks=True,
                          lstrip_blocks=True)


# ======================
# Jinja2 custom filters.
# ======================
environment.filters["integertostring"] = s2.integertostring
environment.filters["rjustify"] = s2.rjustify


# =================
# Jinja2 templates.
# =================
t2 = environment.get_template("T2")
t3 = environment.get_template("T3")


# ==========
# Constants.
# ==========
TABSIZE, RAJUST, TEMPLATE = 10, 25, {"A": t2, "G": t3}


# ================
# Initializations.
# ================
args, d, firstterm, terms, difference, ratio, precision, sequence, series, choice, arguments = [], {}, None, None, None, None, None, None, None, None, parser.parse_args()


# ===============
# Main algorithm.
# ===============


#     ---------------------------
#  1. First term of the sequence.
#     ---------------------------
while not firstterm:
    cls()
    print(TEMPLATE[arguments.type].render())
    firstterm = input("\n   Please enter the first terms of the sequence: ")
    try:
        firstterm = Decimal(firstterm)
    except (ValueError, InvalidOperation):
        firstterm = None


#     --------------------------------
#  2. Number of terms of the sequence.
#     --------------------------------
args.append(("First term", "{:>5}".format(firstterm)))
d["arguments"] = args
while not terms:
    cls()
    print(TEMPLATE[arguments.type].render(**d))
    terms = input("   Please enter the number of terms of the sequence: ")
    try:
        terms = Decimal(terms)
    except (ValueError, InvalidOperation):
        terms = None


#     --------------------------------------------------------------------
#  3. Common difference between two terms if arithmetic sequence expected.
#     --------------------------------------------------------------------
if arguments.type == "A":
    args.append(("Terms\t".expandtabs(TABSIZE), "{:>5}".format(terms)))
    d["arguments"] = args
    while not difference:
        cls()
        print(TEMPLATE[arguments.type].render(**d))
        difference = input("   Please enter the common difference of the sequence: ")
        try:
            difference = Decimal(difference)
        except (ValueError, InvalidOperation):
            difference = None


#     --------------------------------------------------------------
#  4. Common ratio between two terms if geometric sequence expected.
#     --------------------------------------------------------------
elif arguments.type == "G":
    args.append(("Terms\t".expandtabs(TABSIZE), "{:>5}".format(terms)))
    d["arguments"] = args
    while not ratio:
        cls()
        print(TEMPLATE[arguments.type].render(**d))
        ratio = input("   Please enter the common ratio of the sequence: ")
        try:
            ratio = Decimal(ratio)
        except (ValueError, InvalidOperation):
            ratio = None


#     ----------
#  5. Precision.
#     ----------
if arguments.type == "A":
    args.append(("Difference", "{:>5}".format(difference)))
elif arguments.type == "G":
    args.append(("Ratio\t".expandtabs(TABSIZE), "{:>5}".format(ratio)))
d["arguments"] = args
while not precision:
    cls()
    print(TEMPLATE[arguments.type].render(**d))
    precision = input("   Please enter precision: ")
    try:
        precision = int(precision)
    except (ValueError, InvalidOperation):
        precision = None


#     ---------------------------------
#  6. Display elements, series or both?
#     ---------------------------------
args.append(("Precision\t".expandtabs(TABSIZE), "{:>5}".format(precision)))
d["arguments"] = args
while not choice:
    cls()
    print(TEMPLATE[arguments.type].render(**d))
    choice = input("   Display elements [E], series [S] or both [B]: ")
    if choice.upper() not in ["B", "E", "S"]:
        choice = None


#     ----------------
#  7. Compute results.
#     ----------------
if arguments.type == "A":
    arithmetic = s1.ArithmeticSequence(firstterm=firstterm, difference=difference, terms=terms)
    sequence = list(enumerate(["{:>{rajust}.{precision}f}".format(term, rajust=RAJUST, precision=precision) for term in arithmetic.sequence]))
    series = arithmetic.series
elif arguments.type == "G":
    geometric = s1.GeometricSequence(firstterm=firstterm, ratio=ratio, terms=terms)
    sequence = list(enumerate(["{:>{rajust}.{precision}f}".format(term, rajust=RAJUST, precision=precision) for term in geometric.sequence]))
    series = geometric.series
if choice.upper() == "E":
    d["sequence"] = sequence
    d["series"] = None
elif choice.upper() == "S":
    d["sequence"] = None
    d["series"] = "{:.{precision}f}".format(series, precision=precision)
elif choice.upper() == "B":
    d["sequence"] = sequence
    d["series"] = "{:.{precision}f}".format(series, precision=precision)


#     ----------------
#  8. Display results.
#     ----------------
cls()
print(TEMPLATE[arguments.type].render(**d))
input("\n   Press Enter to exit... ")


# ===============
# Exit algorithm.
# ===============
sys.exit(0)
