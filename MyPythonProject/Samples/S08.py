# -*- coding: ISO-8859-1 -*-
import sys

__author__ = 'Xavier ROSSET'


print(sys.stdout.encoding)
print(sys.stdin.encoding)
u = "abcdé"
print(ord(u[-1]))
print(u[-1])
print(chr(233))
