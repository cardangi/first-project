# -*- coding: ISO-8859-1 -*-
from decimal import Decimal
from functools import wraps
import subprocess
import itertools
import argparse
import sys
from .Modules import shared as s1
from .. import shared as s2

__author__ = 'Xavier ROSSET'


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
TITLE, TITLES, SEQUENCES, TABSIZE = {"A": "DISPLAY ARITHMETIC SEQUENCE", "G": "DISPLAY GEOMETRIC SEQUENCE"}, \
                                    ["{0:>10s}".format("indice"), "{0:>18s}".format("element"), "{0:>10s}".format("-"*len("indice")), "{0:>18s}".format("-"*len("element"))], \
                                    {"A": s1.ArithmeticSequence, "G": s1.GeometricSequence}, \
                                    10


# =================
# Initialization 1.
# =================
firstterm, terms, difference, ratio, precision, choice, series, arguments = None, None, None, None, None, None, None, parser.parse_args()


# =================
# Initialization 2.
# =================
header = "{0:>{width}s}\n{1:>{width}s}\n{0:>{width}s}".format("".join(list(itertools.repeat("*", len(TITLE[arguments.type]) + 4))),
                                                              "* {0} *".format(TITLE[arguments.type]),
                                                              width=len(TITLE[arguments.type]) + 4 + 3)


# ========
# Classes.
# ========
class Header(object):
    """
    Docstring.
    """
    def __init__(self, arg):
        self._header = ""
        self.header = arg

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, arg):
        self._header = arg

    def __call__(self, func):

        @wraps(func)
        def wrapper():
            func()
            return "\n{0}".format(self.header)

        return wrapper


class Memoizer(object):
    """
    Docstring.
    """
    def __init__(self):
        self._index = 0
        self._saved = dict()

    def __call__(self, func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            lheader, ldetail, template = func(), "", "{0}\n{1:>{width}s}: {2}"
            for key in sorted(self._saved.keys(), key=int):
                ldetail = template.format(ldetail, self._saved[key][0], self._saved[key][1], width=len(self._saved[key][0]) + 3)
            if args:
                self._index += 1
                self._saved[str(self._index)] = args
                ldetail = template.format(ldetail, args[0], args[1], width=len(args[0]) + 3)
            if kwargs.get("reset", False):
                self._index = 0
                self._saved = dict()
            return "{0}\n\n{1}".format(lheader, ldetail)

        return wrapper


class Sequence(object):

    def __init__(self, arg):
        self._objtype = None
        self.objtype = arg

    def __call__(self, *args):
        return self.objtype(*args)

    @property
    def objtype(self):
        return self._objtype

    @objtype.setter
    def objtype(self, arg):
        self._objtype = arg


# ==========
# Functions.
# ==========
@Memoizer()
@Header(header)
def clearscreen():
    """
    Docstring
    """
    subprocess.run("CLS", shell=True)


# ===============
# Main algorithm.
# ===============
while True:

    #     ---------------------------
    #  1. First term of the sequence.
    #     ---------------------------
    while True:
        print(clearscreen())
        try:
            firstterm = Decimal(input("   Please enter the first terms of the sequence: "))
        except ArithmeticError:
            continue
        else:
            break

    #     --------------------------------
    #  2. Number of terms of the sequence.
    #     --------------------------------
    while True:
        print(clearscreen("First term", firstterm))
        try:
            terms = int(Decimal(input("\n\n   Please enter the number of terms of the sequence: ")))
        except ArithmeticError:
            continue
        else:
            if terms == 0:
                continue
            if arguments.type == "A" and terms > 49999:
                continue
            if arguments.type == "G" and terms > 1499:
                continue
            break

    while True:
        print(clearscreen("Terms\t".expandtabs(TABSIZE), terms))

    #     --------------------------------------------------------------------
    #  3. Common difference between two terms if arithmetic sequence expected.
    #     --------------------------------------------------------------------
        if arguments.type == "A":
            try:
                difference = Decimal(input("\n\n   Please enter the common difference of the sequence: "))
            except ArithmeticError:
                continue
            else:
                if difference.compare(Decimal("0")) == Decimal("0"):
                    continue
                break

    #     --------------------------------------------------------------
    #  4. Common ratio between two terms if geometric sequence expected.
    #     --------------------------------------------------------------
        elif arguments.type == "G":
            try:
                ratio = Decimal(input("\n\n   Please enter the common ratio of the sequence: "))
            except ArithmeticError:
                continue
            else:
                if ratio.compare(Decimal("0")) == Decimal("0"):
                    continue
                if ratio.compare(Decimal("1")) == Decimal("0"):
                    continue
                if ratio.compare(Decimal("99")) == Decimal("1"):
                    continue
                break

    #     ----------
    #  5. Precision.
    #     ----------
    while True:
        if arguments.type == "A":
            print(clearscreen("Difference", difference))
        elif arguments.type == "G":
            print(clearscreen("Ratio\t".expandtabs(TABSIZE), ratio))
        precision = input("\n\n   Please enter precision: ")
        try:
            precision = int(Decimal(precision))
        except ArithmeticError:
            continue
        else:
            break

    #     ---------------------------------
    #  6. Display elements, series or both?
    #     ---------------------------------
    while True:
        print(clearscreen("Precision\t".expandtabs(TABSIZE), precision))
        choice = input("\n\n   Display elements [E], series [S] or both [B]: ")
        if choice.upper() not in ["B", "E", "S"]:
            continue
        break

    #     -----------------
    #  7. Compute sequence.
    #     -----------------

    #  7a. Arithmetic sequence.
    args = tuple()
    if arguments.type == "A":
        args = (firstterm, difference, terms)
    elif arguments.type == "G":
        args = (firstterm, ratio, terms)
    sequence = Sequence(SEQUENCES[arguments.type])(*args)

    #     ----------------
    #  8. Display results.
    #     ----------------
    print(clearscreen(reset=True))

    #  8a. Sequence.
    if choice.upper() in ["B", "E"]:
        print("\n\n\n   The terms of the sequence are:\n\n\n{d[2]}{d[3]}\n{d[0]}{d[1]}\n{d[2]}{d[3]}".format(d=TITLES))
        for index, element in enumerate(sequence.sequence):
            print("{0:>10} {1:>17.{precision}f}".format(index, element, precision=precision))

    #  8b. Series.
    if choice.upper() in ["B", "S"]:
        print("\n\n\n   The sum of the terms is: {0:.{precision}f}".format(sequence.series, precision=precision))

    #     -------------
    #  9. Exit program.
    #     -------------
    while True:
        choice = input("\n\n   Exit program [Y/N]? ")
        if choice.upper() not in s2.ACCEPTEDANSWERS:
            continue
        break
    if choice.upper() == "Y":
        break


# ===============
# Exit algorithm.
# ===============
sys.exit(0)
