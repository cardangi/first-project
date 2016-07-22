# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


def grabdiscnumber(fil, rex):
    match = rex.search(fil)
    if match:
        return True, match.group(1)
    return False, None
