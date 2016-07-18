# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from subprocess import run
from pytz import timezone
import locale
import sys
import os
import re


# =================
# Relative imports.
# =================
from . import shared


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Functions.
# ==========
def pprint(t):
    run("CLS", shell=True)
    if t:
        print(t)


# ==========
# Constants.
# ==========
TABSIZE = 5


# ===================
# Jinja2 environment.
# ===================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_PYTHONPROJECT%"), "Applications", "Templates"), encoding=shared.DFTENCODING), trim_blocks=True, lstrip_blocks=True)


# ======================
# Jinja2 custom filters.
# ======================
environment.filters["integertostring"] = shared.integertostring
environment.filters["rjustify"] = shared.rjustify


# ================
# Jinja2 template.
# ================
template = environment.get_template("T2")


# ================
# Initializations.
# ================
pattern1, pattern2, pattern3, pattern4, pattern5 = r"^(?=\d{{4}}$)(?:{0})$".format(shared.DFTYEARREGEX), \
                                                   r"^(?=\d{{2}}$)(?:{0})$".format(shared.DFTMONTHREGEX), \
                                                   r"^(?=\d{{2}}$)(?:{0})$".format(shared.DFTDAYREGEX), \
                                                   r"^(?=\d{2}$)(?:[01][0-9]|2[0-3])$", \
                                                   r"^(?=\d{2}$)(?:[0-5][0-9])$"
regex1, regex2, regex3, regex4, regex5 = re.compile(pattern1), \
                                         re.compile(pattern2), \
                                         re.compile(pattern3), \
                                         re.compile(pattern4), \
                                         re.compile(pattern5)
step, choice, year, month, day, hours, minutes, seconds, args = 0, "", "", "", "", "", "", "", []


# ===============
# Main algorithm.
# ===============
while True:
    step += 1
    tmpl = template.render(step=step, title="Set year.")

    #     -----------------------------
    #  1. Set year from keyboard input.
    #     -----------------------------
    while True:
        pprint(t=tmpl)
        year = input("\n\n\tPlease enter year: ".expandtabs(TABSIZE))
        if year:
            if not regex1.match(year):
                tmpl = template.render(step=step, title="Set year.", information='"{0}" is not a valid year.'.format(year))
                continue
            break
        year = timezone("UTC").localize(datetime.utcnow()).astimezone(timezone(shared.DFTTIMEZONE)).strftime("%Y")
        break
    args.append("{0}: {1}.".format("Year".ljust(7), year))
    step += 1
    tmpl = template.render(step=step, title="Set month.", information=args)

    #     ------------------------------
    #  2. Set month from keyboard input.
    #     ------------------------------
    while True:
        pprint(t=tmpl)
        month = input("\n\n\tPlease enter month: ".expandtabs(TABSIZE))
        if month:
            month = month.zfill(2)
            if not regex2.match(month):
                tmpl = template.render(step=step, title="Set month.", information='"{0}" is not a valid month.'.format(month))
                continue
            break
        month = timezone("UTC").localize(datetime.utcnow()).astimezone(timezone(shared.DFTTIMEZONE)).strftime("%m")
        break
    args.append("{0}: {1}.".format("Month".ljust(7), month))
    step += 1
    tmpl = template.render(step=step, title="Set day.", information=args)

    #     ----------------------------
    #  3. Set day from keyboard input.
    #     ----------------------------
    while True:
        pprint(t=tmpl)
        day = input("\n\n\tPlease enter day: ".expandtabs(TABSIZE))
        if day:
            day = day.zfill(2)
            if not regex3.match(day):
                tmpl = template.render(step=step, title="Set day.", information='"{0}" is not a valid day.'.format(day))
                continue
            break
        day = timezone("UTC").localize(datetime.utcnow()).astimezone(timezone(shared.DFTTIMEZONE)).strftime("%d")
        break
    args.append("{0}: {1}.".format("Day".ljust(7), day))
    step += 1
    tmpl = template.render(step=step, title="Set hours.", information=args)

    #     ------------------------------
    #  4. Set hours from keyboard input.
    #     ------------------------------
    while True:
        pprint(t=tmpl)
        hours = input("\n\n\tPlease enter hours: ".expandtabs(TABSIZE))
        if hours:
            hours = hours.zfill(2)
            if not regex4.match(hours):
                tmpl = template.render(step=step, title="Set hours.", information='"{0}" are not valid hours.'.format(hours))
                continue
            break
        hours = timezone("UTC").localize(datetime.utcnow()).astimezone(timezone(shared.DFTTIMEZONE)).strftime("%H")
        break
    args.append("{0}: {1}.".format("Hours".ljust(7), hours))
    step += 1
    tmpl = template.render(step=step, title="Set minutes.", information=args)

    #     --------------------------------
    #  5. Set minutes from keyboard input.
    #     --------------------------------
    while True:
        pprint(t=tmpl)
        minutes = input("\n\n\tPlease enter minutes: ".expandtabs(TABSIZE))
        if minutes:
            minutes = minutes.zfill(2)
            if not regex5.match(minutes):
                tmpl = template.render(step=step, title="Set minutes.", information='"{0}" are not valid minutes.'.format(minutes))
                continue
            break
        minutes = timezone("UTC").localize(datetime.utcnow()).astimezone(timezone(shared.DFTTIMEZONE)).strftime("%M")
        break
    args.append("{0}: {1}.".format("Minutes".ljust(7), minutes))
    step += 1
    tmpl = template.render(step=step, title="Set seconds.", information=args)

    #     --------------------------------
    #  6. Set seconds from keyboard input.
    #     --------------------------------
    while True:
        pprint(t=tmpl)
        seconds = input("\n\n\tPlease enter seconds: ".expandtabs(TABSIZE))
        if seconds:
            seconds = seconds.zfill(2)
            if not regex5.match(seconds):
                tmpl = template.render(step=step, title="Set seconds.", information='"{0}" are not valid seconds.'.format(seconds))
                continue
            break
        seconds = timezone("UTC").localize(datetime.utcnow()).astimezone(timezone(shared.DFTTIMEZONE)).strftime("%S")
        break
    args.append("{0}: {1}.".format("Seconds".ljust(7), seconds))

    #     ---------------
    #  7. Get unix epoch.
    #     ---------------
    dtobject = timezone("Europe/Paris").localize(datetime(year=int(year), month=int(month), day=int(day), hour=int(hours), minute=int(minutes), second=int(seconds)))

    #     -------------------
    #  8. Display unix epoch.
    #     -------------------
    step += 1
    tmpl = template.render(step=step,
                           title="Get unix epoch.",
                           information=list(("{0}: {1}".format("Date".ljust(TABSIZE), shared.dateformat(dtobject, shared.TEMPLATE4)), "{0}: {1}".format("Epoch".ljust(TABSIZE), int(dtobject.timestamp()))))
                           )
    while True:
        pprint(t=tmpl)
        choice = input("\n\n\tWould you like to exit program [Y/N]? ".expandtabs(TABSIZE))
        if choice.upper() in shared.ACCEPTEDANSWERS:
            break
    if choice.upper() == "Y":
        break
    step = 0
    args.clear()


# =============
# Exit program.
# =============
sys.exit(0)
