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


# ========
# Classes.
# ========
class FirstDecorator(object):
    """
    Docstring.
    """
    def __init__(self, datatoprint):
        self.datatoprint = datatoprint

    def __call__(self, func):

        @wraps(func)
        def noname():
            func()
            return self.datatoprint

        return noname



class SecondDecorator(object):
    """
    Docstring.
    """
    def __init__(self):
        self.index = 0
        self.saved = dict()

    def __call__(self, func):

        @wraps(func)
        def noname(*args):
            template = "{0:>{width}s}: {1}\n"
            func()
            for key in sorted(self.saved.keys(), key=int):
                return template.format(self.saved[key][0], self.saved[key][1], width=len(self.saved[key][0]) + 3))
            if args:
                self.index += 1
                self.saved[str(self.index)] = args
                return template.format(args[0], args[1], width=len(args[0]) + 3))

        return noname


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


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("type", help="type of the sequence: arithmetic or geometric.", choices=["A", "G"])


# ==========
# Constants.
# ==========
TITLE, TITLES = {"A": "DISPLAY ARITHMETIC SEQUENCE", "G": "DISPLAY GEOMETRIC SEQUENCE"}, ["{0:>10s}".format("indice"),
                                                                                          "{0:>18s}".format("element"),
                                                                                          "{0:>10s}".format("-"*len("indice")),
                                                                                          "{0:>18s}".format("-"*len("element"))]


# ================
# Initializations.
# ================
firstterm, terms, difference, ratio, precision, choice, series, arguments = None, None, None, None, None, None, None, parser.parse_args()


# ===============
# Main algorithm.
# ===============
header = "{0:>{width}s}\n{1:>{width}s}\n{0:>{width}s}\n\n".format("".join(list(itertools.repeat("*", len(TITLE[arguments.type]) + 4))),
                                                                  "* {0} *".format(TITLE[arguments.type]),
                                                                  width=len(TITLE[arguments.type]) + 4 + 3)
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
        print(clearscreen("Terms\t".expandtabs(13), terms))

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
        FirstDecorator(header)(clearscreen)()
        if arguments.type == "A":
            SecondDecorator(("First term", firstterm), ("Terms\t".expandtabs(13), terms), ("Difference", difference))(FirstDecorator(header)(clearscreen))()
        elif arguments.type == "G":
            SecondDecorator(("First term", firstterm), ("Terms\t".expandtabs(13), terms), ("Ratio\t".expandtabs(13), ratio))(FirstDecorator(header)(clearscreen))()
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
        if arguments.type == "A":
            SecondDecorator(("First term", firstterm), ("Terms\t".expandtabs(13), terms), ("Difference", difference), ("Precision\t".expandtabs(13), precision))(FirstDecorator(header)(clearscreen))()
        elif arguments.type == "G":
            SecondDecorator(("First term", firstterm), ("Terms\t".expandtabs(13), terms), ("Ratio\t".expandtabs(13), ratio), ("Precision\t".expandtabs(13), precision))(FirstDecorator(header)(clearscreen))()
        choice = input("   Display elements [E], series [S] or both [B]: ")
        if choice.upper() not in ["B", "E", "S"]:
            continue
        break

    #     ----------------
    #  7. Display results.
    #     ----------------
    while True:

        if arguments.type == "A":
            SecondDecorator(("First term", firstterm), ("Terms\t".expandtabs(13), terms), ("Difference", difference), ("Precision\t".expandtabs(13), precision))(FirstDecorator(header)(clearscreen))()
        elif arguments.type == "G":
            SecondDecorator(("First term", firstterm), ("Terms\t".expandtabs(13), terms), ("Ratio\t".expandtabs(13), ratio), ("Precision\t".expandtabs(13), precision))(FirstDecorator(header)(clearscreen))()

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
