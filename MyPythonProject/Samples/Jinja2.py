# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


from jinja2 import Environment, FileSystemLoader


environment = Environment(loader=FileSystemLoader(r"g:\computing\mypythonproject\applications\templates"), trim_blocks=True, lstrip_blocks=True)
template = environment.get_template("Sample")


print(template.render(iterable=["text_01 ", "text_02 ", "text_03 "], condition=False))
