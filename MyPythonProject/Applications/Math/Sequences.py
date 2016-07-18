# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
import subprocess
import argparse
import sys
import os


# =================
# Relative imports.
# =================
from .Modules import shared


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
TITLEA, TITLEG = "DISPLAY ARITHMETIC SEQUENCE", "DISPLAY GEOMETRIC SEQUENCE"


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
        print("   Terms: {0}\n".format(terms))
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
        print("   Terms: {0}\n".format(terms))
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
    print("   Terms: {0}".format(terms))
    if arguments.type == "A":
        print("   Difference: {0}\n".format(difference))
    if arguments.type == "G":
        print("   Ratio: {0}\n".format(ratio))
    choice = input("   Display elements [E], series [S] or both [B]: ")
    if choice.upper() not in ["B", "E", "S"]:
        choice = None


#     ----------------
#  6. Display results.
#     ----------------
displayheader(head=header)
print("   First term: {0}".format(firstterm))
print("   Terms: {0}".format(terms))
if arguments.type == "A":
    print("   Difference: {0}".format(difference))
if arguments.type == "G":
    print("   Ratio: {0}".format(ratio))
if choice.upper() in ["B", "E"]:
    print("\n\n   The terms of the sequence are:\n\n\n{2}{3}\n{0}{1}\n{2}{3}".format("indice".upper().rjust(10), "element".upper().rjust(18), ("-"*len("indice")).rjust(10), ("-"*len("element")).rjust(18)))

#  6a. Arithmetic sequence.
if arguments.type == "A":
    if choice.upper() in ["B", "E"]:
        for i in shared.arithmeticsequence(firstterm=firstterm, difference=difference, terms=terms):
            print("{0}. {1}".format(str(j).rjust(9), ("%.2f" % i).rjust(17)))
            j += 1
    if choice.upper() in ["B", "S"]:
        series = shared.arithmeticseries(firstterm=firstterm, difference=difference, terms=terms)

#  6b. Geometric sequence.
elif arguments.type == "G":
    if choice.upper() in ["B", "E"]:
        for i in shared.geometricsequence(firstterm=firstterm, ratio=ratio, terms=terms):
            print("{0}. {1}".format(str(j).rjust(9), ("%.2f" % i).rjust(17)))
            j += 1
    if choice.upper() in ["B", "S"]:
        series = shared.geometricseries(firstterm=firstterm, ratio=ratio, terms=terms)

#  6c. Series if required.
if choice.upper() in ["B", "S"]:
    print("\n\n   The sum of the terms is: %.2f\n\n" % series)
if choice.upper() == "E":
    print("\n\n")


#     -------------
#  7. Exit program.
#     -------------
sys.exit(0)
