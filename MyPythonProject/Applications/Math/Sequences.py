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


# ==========
# Constants.
# ==========
TITLE, TITLES, TABSIZE = {"A": "DISPLAY ARITHMETIC SEQUENCE", "G": "DISPLAY GEOMETRIC SEQUENCE"}, \
                         ["{0:>10s}".format("indice"), "{0:>18s}".format("element"), "{0:>10s}".format("-"*len("indice")), "{0:>18s}".format("-"*len("element"))], \
                         13


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
class FirstDecorator(object):
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
            return "\n{0}\n\n".format(self.header)

        return wrapper


class SecondDecorator(object):
    """
    Docstring.
    """
    def __init__(self):
        self._index = 0
        self._saved = dict()

    def __call__(self, func):

        @wraps(func)
        def wrapper(*args):
            result = func()
            for key in sorted(self._saved.keys(), key=int):
                result = "{0}\n{1:>{width}s}: {2}".format(result, self._saved[key][0], self._saved[key][1], width=len(self._saved[key][0]) + 3)
            if args:
                self._index += 1
                self._saved[str(self._index)] = args
                result = "{0}\n{1:>{width}s}: {2}\n\n".format(result, args[0], args[1], width=len(args[0]) + 3)
            return result

        return wrapper


# ==========
# Functions.
# ==========
@SecondDecorator()
@FirstDecorator(header)
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
            terms = int(Decimal(input("   Please enter the number of terms of the sequence: ")))
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
                difference = Decimal(input("   Please enter the common difference of the sequence: "))
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
                ratio = Decimal(input("   Please enter the common ratio of the sequence: "))
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
            print(clearscreen("Ration\t".expandtabs(TABSIZE), ratio))
        precision = input("   Please enter precision: ")
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
        choice = input("   Display elements [E], series [S] or both [B]: ")
        if choice.upper() not in ["B", "E", "S"]:
            continue
        break

    #     ----------------
    #  7. Display results.
    #     ----------------
    while True:
        print(clearscreen())

        if choice.upper() in ["B", "E"]:
            print("\n\n   The terms of the sequence are:\n\n\n{d[2]}{d[3]}\n{d[0]}{d[1]}\n{d[2]}{d[3]}".format(d=TITLES))

        #  7a. Arithmetic sequence.
        if arguments.type == "A":
            sequence = s1.ArithmeticSequence(firstterm=firstterm, difference=difference, terms=terms)

        #  7b. Geometric sequence.
        elif arguments.type == "G":
            sequence = s1.GeometricSequence(firstterm=firstterm, ratio=ratio, terms=terms)

        #  7c. Sequence.
        if choice.upper() in ["B", "E"]:
            for index, element in enumerate(sequence.sequence):
                print("{0:>10} {1:>17.{precision}f}".format(index, element, precision=precision))
        if choice.upper() in ["B", "S"]:
            series = sequence.series

        #  7d. Series.
        print("\n\n")
        if choice.upper() in ["B", "S"]:
            print("   The sum of the terms is: {0:.{precision}f}\n\n".format(series, precision=precision))
        break

    #     -------------
    #  8. Exit program.
    #     -------------
    while True:
        choice = input("   Exit program [Y/N]? ")
        if choice.upper() not in s2.ACCEPTEDANSWERS:
            continue
        break
    if choice.upper() == "Y":
        break


# ===============
# Exit algorithm.
# ===============
sys.exit(0)
