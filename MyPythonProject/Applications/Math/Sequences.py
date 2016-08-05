# -*- coding: ISO-8859-1 -*-
import subprocess
import argparse
import sys
import os
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
TITLEA, TITLEG, TITLES = "DISPLAY ARITHMETIC SEQUENCE", "DISPLAY GEOMETRIC SEQUENCE", ["{:>10}".format("indice"), "{:>18}".format("element"), "{:>10}".format("-"*len("indice")), "{:>18}".format("-"*len("element"))]


# ================
# Initializations.
# ================
j, firstterm, series, stop, terms, difference, ratio, header, arguments = 0, 0, 0, False, None, None, None, None, parser.parse_args()
if arguments.type == "A":
    header = "{0}\n{1}\n{0}\n\n".format(("*"*(len(TITLEA) + 4)).rjust(len(TITLEA) + 7), "* {0} *".format(TITLEA).rjust(len(TITLEA) + 7))
if arguments.type == "G":
    header = "{0}\n{1}\n{0}\n\n".format(("*"*(len(TITLEG) + 4)).rjust(len(TITLEG) + 7), "* {0} *".format(TITLEG).rjust(len(TITLEG) + 7))


# ===============
# Main algorithm.
# ===============


#     ---------------------------
#  1. First term of the sequence.
#     ---------------------------
while not stop:
    displayheader(head=header)
    firstterm = input("   Please enter the first terms of the sequence: ")
    try:
        firstterm = int(firstterm)
        stop = True
    except ValueError:
        pass


#     --------------------------------
#  2. Number of terms of the sequence.
#     --------------------------------
while not terms:
    displayheader(head=header)
    print("   First term: {0}\n".format(firstterm))
    terms = input("   Please enter the number of terms of the sequence: ")
    try:
        terms = int(terms)
    except ValueError:
        terms = None


#     --------------------------------------------------------------------
#  3. Common difference between two terms if arithmetic sequence expected.
#     --------------------------------------------------------------------
if arguments.type == "A":
    while not difference:
        displayheader(head=header)
        print("   First term: {0}".format(firstterm))
        print("   Terms\t: {0}\n".format(terms).expandtabs(13))
        difference = input("   Please enter the common difference of the sequence: ")
        try:
            difference = int(difference)
        except ValueError:
            difference = None


#     --------------------------------------------------------------
#  4. Common ratio between two terms if geometric sequence expected.
#     --------------------------------------------------------------
elif arguments.type == "G":
    while not ratio:
        displayheader(head=header)
        print("   First term: {0}".format(firstterm))
        print("   Terms\t: {0}\n".format(terms).expandtabs(13))
        ratio = input("   Please enter the common ratio of the sequence: ")
        try:
            ratio = int(ratio)
        except ValueError:
            ratio = None


#     ---------------------------------
#  5. Display elements, series or both?
#     ---------------------------------
choice = None
while not choice:
    displayheader(head=header)
    print("   First term: {0}".format(firstterm))
    print("   Terms\t: {0}".format(terms).expandtabs(13))
    if arguments.type == "A":
        print("   Difference\t: {0}\n".format(difference).expandtabs(13))
    if arguments.type == "G":
        print("   Ratio\t: {0}\n".format(ratio).expandtabs(13))
    choice = input("   Display elements [E], series [S] or both [B]: ")
    if choice.upper() not in ["B", "E", "S"]:
        choice = None


#     ----------------
#  6. Display results.
#     ----------------
displayheader(head=header)
print("   First term: {0}".format(firstterm))
print("   Terms\t: {0}".format(terms).expandtabs(13))
if arguments.type == "A":
    print("   Difference\t: {0}".format(difference).expandtabs(13))
if arguments.type == "G":
    print("   Ratio\t: {0}".format(ratio).expandtabs(13))
if choice.upper() in ["B", "E"]:
    print("\n\n   The terms of the sequence are:\n\n\n{d[2]}{d[3]}\n{d[0]}{d[1]}\n{d[2]}{d[3]}".format(d=TITLES))

#  6a. Arithmetic sequence.
if arguments.type == "A":
    arithmetic = shared.ArithmeticSequence(firstterm=firstterm, difference=difference, terms=terms)
    if choice.upper() in ["B", "E"]:
        for i in arithmetic.sequence:
            print("{0}. {1}".format(str(j).rjust(9), ("%.2f" % i).rjust(17)))
            j += 1
    if choice.upper() in ["B", "S"]:
        series = arithmetic.series

#  6b. Geometric sequence.
elif arguments.type == "G":
    geometric = shared.GeometricSequence(firstterm=firstterm, difference=difference, terms=terms)
    if choice.upper() in ["B", "E"]:
        for i in geometric.sequence:
            print("{0}. {1}".format(str(j).rjust(9), ("%.2f" % i).rjust(17)))
            j += 1
    if choice.upper() in ["B", "S"]:
        series = geometric.series

#  6c. Series if required.
if choice.upper() in ["B", "S"]:
    print("\n\n   The sum of the terms is: %.2f\n\n" % series)
if choice.upper() == "E":
    print("\n\n")


#     -------------
#  7. Exit program.
#     -------------
sys.exit(0)
