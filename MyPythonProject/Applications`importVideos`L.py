# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# ===================
# Absolute import(s).
# ===================
import os
import subprocess
from string import Template
from contextlib import contextmanager


# ==========
# Functions.
# ==========
@contextmanager
def chgcurdir(d):
    wcdir = os.getcwd()
    os.chdir(d)
    yield
    os.chdir(wcdir)


# ==========
# Templates.
# ==========
t1 = Template('python -m Applications.importVideos2 "$source" --dst "$destination"')
t2 = Template("$command --test")
t3 = Template("$command --extensions $extensions")

# ==========
# Constants.
# ==========
ARGUMENTS = os.path.join(os.path.expandvars("%TEMP%"), "arguments")


# ================
# Initializations.
# ================
directory, extensions, arguments = "", "", []


# ===============
# Main algorithm.
# ===============
with chgcurdir(os.path.expandvars("%_PYTHONPROJECT%")):
    while True:
        process1 = subprocess.run(["python", "-m", "Applications.importVideos1"])
        if process1.returncode == 0:
            if os.path.exists(ARGUMENTS):
                with open(ARGUMENTS, encoding="ISO-8859-1") as fr:
                    for line in fr:
                        parts = line.splitlines()[0].split(";")
                        if len(parts) > 3:
                            extensions = parts[3].split(";")
                        args = t1.substitute(source=parts[0], destination=parts[1])
                        if parts[2].upper() == "Y":
                            args = t2.substitute(command=args)
                        if extensions:
                            args = t3.substitute(command=args, extensions=" ".join(extensions))
                        process2 = subprocess.run(args)
        break
