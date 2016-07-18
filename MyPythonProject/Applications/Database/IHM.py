# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# =================
# Absolute imports.
# =================
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from string import Template
from pytz import timezone
import subprocess
import logging
import sqlite3
import locale
import shlex
import sys
import os
import re


# =================
# Relative imports.
# =================
from .. import shared


# ==========================
# Define French environment.
# ==========================
locale.setlocale(locale.LC_ALL, "")


# ==========
# Constants.
# ==========
HEADER, TITLES, SCRIPTS, EXIT = "work with database", \
                                {"1": "Set table.", "2": "Set statement.", "3": "Set record unique ID."}, \
                                {"Backup": "dbBackup", "LastRunDates": "dbLastRunDates"}, \
                                {"N": shared.BACK, "Y": shared.EXIT}


# ================
# Initializations.
# ================
step, uid, statement = 0, 0, 0
table, choice, timestamp, step4, step5, ids = "", "", "", "Y", "N", []


# ====================
# Regular expressions.
# ====================
rex1 = re.compile(r"^\d+$")
rex2 = re.compile(r"^(\d+)\b\-\b(\d+)$")
rex3 = re.compile(r"^(\b(\d)+\b(\s+|\-)?)+$")
rex4 = re.compile(r"^\d{10}$")


# ================
# Local templates.
# ================
tmpl1 = Template("python -m Applications.Database.$script $statement")
tmpl2 = Template("$command --uid")
tmpl3 = Template("$command $ids")
tmpl4 = Template("$command --timestamp $timestamp")


# ==========
# Functions.
# ==========
def pprint(t=None):
    subprocess.run("CLS", shell=True)
    if t:
        print(t)


# ======================
# Jinja2 environment(s).
# ======================
environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_pythonproject%"), "Applications", "Database", "Templates"), encoding=shared.DFTENCODING), trim_blocks=True, lstrip_blocks=True)


# ========================
# Jinja2 custom filter(s).
# ========================
environment.filters["integertostring"] = shared.integertostring
environment.filters["ljustify"] = shared.ljustify
environment.filters["rjustify"] = shared.rjustify
environment.filters["fillwith"] = shared.fillwith


# ===================
# Jinja2 template(s).
# ===================
template = environment.get_template("tmpl01")


# ========
# Logging.
# ========
logger = logging.getLogger("%s.%s" % (__package__, os.path.basename(__file__)))


# ===============
# Main algorithm.
# ===============


#     --------------
#  1. Start logging.
#     --------------
logger.info("{0} {1} {0}".format("="*50, shared.dateformat(datetime.now(tz=timezone(shared.DFTTIMEZONE)), shared.TEMPLATE1)))
logger.info('START "%s".' % (os.path.basename(__file__),))

#     ----------
#  2. Set table.
#     ----------
tables = {"1": "Backup", "2": "LastRunDates"}
step += 1
tmpl = template.render(header=HEADER, step=step, title=TITLES[str(step)], menu=tables)
while True:
    pprint(tmpl)
    choice = input("\n\n\n     Please choose table: ")
    if choice in tables.keys():
        table = tables[choice]
        break
logger.debug("Table\t: {0}.".format(table).expandtabs(5))


#     --------------
#  3. Set statement.
#     --------------
statements = {"1": "Delete", "2": "Update"}
step += 1
tmpl = template.render(header=HEADER, step=step, title=TITLES[str(step)], message=list(("Table: {0}.".format(table),)), menu=statements)
while True:
    pprint(t=tmpl)
    choice = input("\n\n\n     Please choose statement: ")
    if choice in statements.keys():
        statement = statements[choice]
        break
logger.debug("Statement\t: {0}.".format(statement).expandtabs(5))


#     ---------------------
#  4. Set record unique ID.
#     ---------------------
if statement.lower() == "delete":
    step += 1
    tmpl = template.render(header=HEADER, step=step, title=TITLES[str(step)], message=list(("Table    : {0}.".format(table), "Statement: {0}.".format(statement))))
    while True:
        pprint(tmpl)
        choice = input("\n\n\n     Would you like to enter record unique ID [Y/N]? ")
        if choice.upper() not in shared.ACCEPTEDANSWERS:
            continue
        break
    step4 = choice.upper()

if step4 == "Y":
    step += 1
    tmpl = template.render(header=HEADER, step=step, title=TITLES[str(step)], message=list(("Table    : {0}.".format(table), "Statement: {0}.".format(statement))))
    while True:
        pprint(tmpl)
        uid = input("\n\n\n     Please enter record unique ID [e.g. 1 2 3 4 5 6-10]: ")
        if not uid:
            tmpl = template.render(header=HEADER, step=step, title=TITLES[str(step)], message=list(("Table    : {0}.".format(table), "Statement: {0}.".format(statement))))
        elif uid:
            if not rex3.match(uid):
                tmpl = template.render(header=HEADER,
                                       step=step,
                                       title=TITLES[str(step)],
                                       message=list(("Table    : {0}.".format(table),
                                                     "Statement: {0}.".format(statement),
                                                     "ID       : {0}.".format(uid),
                                                     "\n     Input doesn't match the expected pattern."))
                                       )
                continue
            for item in uid.split():
                match1 = rex1.match(item)
                match2 = rex2.match(item)
                if any((match1, match2)):
                    if match1:
                        conn = sqlite3.connect(shared.DATABASE)
                        if conn.cursor().execute("SELECT count(*) FROM {0} WHERE id=?".format(table), (int(item),)).fetchone()[0]:
                            ids.append(int(item))
                        conn.close()
                    elif match2:
                        for i in range(int(match2.group(1)), int(match2.group(2)) + 1):
                            conn = sqlite3.connect(shared.DATABASE)
                            if conn.cursor().execute("SELECT count(*) FROM {0} WHERE id=?".format(table), (i,)).fetchone()[0]:
                                ids.append(i)
                            conn.close()
            if not ids:
                tmpl = template.render(header=HEADER,
                                       step=step,
                                       title=TITLES[str(step)],
                                       message=list(("Table    : {0}.".format(table),
                                                     "Statement: {0}.".format(statement),
                                                     "ID       : {0}.".format(uid),
                                                     "\n     Input isn't coherent."))
                                       )
                continue
            break
if ids:
    logger.debug("IDs\t: {0}.".format(" ".join([str(item) for item in ids])).expandtabs(10))


#     --------------
#  5. Set timestamp.
#     --------------
if statement.lower() == "update" and table.lower() in ["lastrundates", "backup"]:
    step += 1
    tmpl = template.render(header=HEADER,
                           step=step, title="Set timestamp.",
                           message=list(("Table    : {0}.".format(table),
                                         "Statement: {0}.".format(statement),
                                         "ID       : {0}.".format(uid),
                                         "\n     Chosen records will be updated to the current local system datetime by default or to a given specific datetime."
                                         ))
                           )
    while True:
        pprint(tmpl)
        choice = input("\n\n\n     Would you like to enter a specific datetime [Y/N]? ")
        if choice.upper() not in shared.ACCEPTEDANSWERS:
            continue
        break
    step5 = choice.upper()

if step5 == "Y":
    step += 1
    tmpl = template.render(header=HEADER, step=step, title="Set timestamp.", message=list(("Table    : {0}.".format(table), "Statement: {0}.".format(statement), "ID       : {0}.".format(uid))))
    while True:
        pprint(tmpl)
        timestamp = input("\n\n\n     Please enter correponding timestamp [e.g. 1464770190]: ")
        if not timestamp:
            tmpl = template.render(header=HEADER, step=step, title="Set timestamp.", message=list(("Table    : {0}.".format(table), "Statement: {0}.".format(statement), "ID       : {0}.".format(uid))))
        elif timestamp:
            if not rex4.match(timestamp):
                tmpl = template.render(header=HEADER,
                                       step=step,
                                       title="Set timestamp.",
                                       message=list(("Table    : {0}.".format(table),
                                                     "Statement: {0}.".format(statement),
                                                     "ID       : {0}.".format(uid),
                                                     "\n     Input doesn't match the expected pattern."))
                                       )
                continue
            break
if timestamp:
    logger.debug("Timestamp\t: {0}.".format(timestamp).expandtabs(10))


#     --------------
#  6. Build command.
#     --------------
command = tmpl1.substitute(script=SCRIPTS[table], statement=statement.lower())
if ids:
    if statement.lower() == "delete":
        command = tmpl2.substitute(command=command)
    command = tmpl3.substitute(command=command, ids=" ".join([str(item) for item in ids]))
if timestamp:
    command = tmpl4.substitute(command=command, timestamp=timestamp)


#     --------------
#  7. Check command.
#     --------------
step += 1
tmpl = template.render(header=HEADER, step=step, title="Check command.", message=list(('The following command will be executed: {0}'.format(command),)))
while True:
    pprint(tmpl)
    choice = input("\n\n\n     Would you like to run command [Y/N]? ")
    if choice.upper() not in shared.ACCEPTEDANSWERS:
        continue
    break

#  5a. Cancel command.
if choice.upper() == "N":
    step += 1
    tmpl = template.render(header=HEADER, step=step, title="Exit program.")

#  5b. Confirm command.
elif choice.upper() == "Y":
    step += 1
    tmpl = template.render(header=HEADER, step=step, title="Exit program.")
    logger.info("Start new process.")
    logger.info("Run command described by: {0}".format(command))
    process = subprocess.run(command, shell=True)
    logger.debug("subprocess module returned {0} as code.".format(process.returncode))
    if process.returncode != 0:
        tmpl = template.render(header=HEADER,
                               step=step,
                               title="Exit program.",
                               message=list(("Table    : {0}.".format(table),
                                             "Statement: {0}.".format(statement),
                                             "ID       : {0}.".format(uid),
                                             "Command  : {0}.".format(command),
                                             "\n    An issue occurred with the command. See log for more details.")
                                            )
                               )


#     ------------
#  8. End logging.
#     ------------
logger.info('END "%s".' % (os.path.basename(__file__),))


#     -------------
#  9. Exit program.
#     -------------
while True:
    pprint(tmpl)
    choice = input("\n\n\n     Would you like to exit program [Y/N]? ")
    if choice.upper() not in shared.ACCEPTEDANSWERS:
        continue
    break
pprint()
sys.exit(EXIT[choice.upper()])
