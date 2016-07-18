# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


from jinja2 import Environment, FileSystemLoader
from Applications import shared
import os


environment = Environment(loader=FileSystemLoader(os.path.join(os.path.expandvars("%_pythonproject%"), "Applications", "AudioFiles", "Templates"), encoding=shared.DFTENCODING), trim_blocks=True, lstrip_blocks=True)
environment.globals["now"] = shared.now()
environment.globals["copyright"] = shared.COPYRIGHT
environment.filters["integertostring"] = shared.integertostring
environment.filters["repeatelement"] = shared.repeatelement
environment.filters["sortedlist"] = shared.sortedlist
environment.filters["ljustify"] = shared.ljustify
environment.filters["rjustify"] = shared.rjustify
template = environment.get_template("T1")


class Header:
    pass


header = Header()
header.main = "Main title"
header.step = 1
header.title = ""
print(template.render(header=header))

header.step = 2
header.title = "TITLE 2"
print(template.render(header=header))
