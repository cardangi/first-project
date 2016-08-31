# -*- coding: ISO-8859-1 -*-
from decimal import Decimal
import subprocess
import argparse
import sys
from .Modules import shared

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def displayheader(head=None):
    subprocess.run("CLS", shell=True)
    if head:
        print("\n{0}".format(head))


# =================
# Arguments parser.
# =================
parser = argparse.ArgumentParser()
parser.add_argument("type", help="type of the sequence: arithmetic or geometric.", choices=["A", "G"])


# ==========
# Constants.
# ==========
TITLE, TITLES = {"A": "DISPLAY ARITHMETIC SEQUENCE", "G": "DISPLAY GEOMETRIC SEQUENCE"}, ["{0:>10}".format("indice"), "{0:>18}".format("element"), "{0:>10}".format("-"*len("indice")), "{0:>18}".format("-"*len("element"))]


# ================
# Initializations.
# ================
header, arguments = "{0:>{width1}s}\n{1:>{width2}s}\n{0:>{width1}s}\n\n".format("".join(list(itertools.repeat("*", len(TITLE[arguments.type]) + 4))), "* {0} *".format(TITLE[arguments.type]), width1=len(TITLE[arguments.type]) + 4 + 3, width2=len(TITLE[arguments.type]) + 3), parser.parse_args()


# ===============
# Main algorithm.
# ===============


#     ---------------------------
#  1. First term of the sequence.
#     ---------------------------
while True:
    displayheader(head=header)
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
    displayheader(head=header)
    print("   First term: {0}\n".format(firstterm))
    try:
        terms = int(Decimal(input("   Please enter the number of terms of the sequence: ")))
    except ArithmeticError:
        continue
    else:
        if arguments.type == "A" and terms > 49999:
            continue
        if arguments.type == "G" and terms > 1499:
            continue
        break


#     --------------------------------------------------------------------
#  3. Common difference between two terms if arithmetic sequence expected.
#     --------------------------------------------------------------------
if arguments.type == "A":
    while True:
        displayheader(head=header)
        print("   First term: {0}".format(firstterm))
        print("   Terms\t: {0}\n".format(terms).expandtabs(13))
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
    while not ratio:
        displayheader(head=header)
        print("   First term: {0}".format(firstterm))
        print("   Terms\t: {0}\n".format(terms).expandtabs(13))
        try:
            ratio = Decimal(input("   Please enter the common ratio of the sequence: "))
        except ArithmeticError:
            continue
        else:
            if ratio.compare(Decimal("0")) == Decimal("0"):
                continue
            if ratio.compare(Decimal("99")) == Decimal("1"):
                continue
            break


#     ----------
#  5. Precision.
#     ----------
while True:
    displayheader(head=header)
    print("   First term: {0}".format(firstterm))
    print("   Terms\t: {0}".format(terms).expandtabs(13))
    if arguments.type == "A":
        print("   Difference: {0}\n".format(difference).expandtabs(13))
    elif arguments.type == "G":
        print("   Ratio\t: {0}\n".format(ratio).expandtabs(13))
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
    displayheader(head=header)
    print("   First term: {0}".format(firstterm))
    print("   Terms\t: {0}".format(terms).expandtabs(13))
    if arguments.type == "A":
        print("   Difference: {0}".format(difference).expandtabs(13))
    elif arguments.type == "G":
        print("   Ratio\t: {0}".format(ratio).expandtabs(13))
    print("   Precision\t: {0}\n".format(precision).expandtabs(13))
    choice = input("   Display elements [E], series [S] or both [B]: ")
    if choice.upper() not in ["B", "E", "S"]:
        continue
    break


#     ----------------
#  7. Display results.
#     ----------------
displayheader(head=header)
print("   First term: {0}".format(firstterm))
print("   Terms\t: {0}".format(terms).expandtabs(13))
if arguments.type == "A":
    print("   Difference: {0}".format(difference).expandtabs(13))
if arguments.type == "G":
    print("   Ratio\t: {0}".format(ratio).expandtabs(13))
print("   Precision\t: {0}".format(precision).expandtabs(13))
if choice.upper() in ["B", "E"]:
    print("\n\n   The terms of the sequence are:\n\n\n{d[2]}{d[3]}\n{d[0]}{d[1]}\n{d[2]}{d[3]}".format(d=TITLES))

while True:

    #  7a. Arithmetic sequence.
    if arguments.type == "A":
        try:
            arithmetic = shared.ArithmeticSequence(firstterm=firstterm, difference=difference, terms=terms)
        except ValueError:
            break
        else:
            if choice.upper() in ["B", "E"]:
                for index, element in enumerate(arithmetic.sequence):
                    print("{0:>9}. {1:>17.{precision}f}".format(index, element, precision=precision))
            if choice.upper() in ["B", "S"]:
                series = arithmetic.series

    #  7b. Geometric sequence.
    elif arguments.type == "G":
        try:
            geometric = shared.GeometricSequence(firstterm=firstterm, ratio=ratio, terms=terms)
        except ValueError:
            break
        else:
            if choice.upper() in ["B", "E"]:
                for index, element in enumerate(geometric.sequence):
                    print("{0:>9}. {1:>17.{precision}f}".format(index, element, precision=precision))
            if choice.upper() in ["B", "S"]:
                series = geometric.series

    #  7c. Series if required.
    if choice.upper() in ["B", "S"]:
        print("\n\n   The sum of the terms is: {0:.{precision}f}\n\n".format(series, precision=precision))
    if choice.upper() == "E":
        print("\n\n")


#     -------------
#  8. Exit program.
#     -------------
sys.exit(0)
