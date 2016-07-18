# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


import operator


x = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # [False, False, False]
y = 'OK'
if any(not operator.lt(i, 10) for i in x):
    y = 'KO'
print(y)

x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # [False, False, False, True]
y = 'OK'
if any(not operator.lt(i, 10) for i in x):
    y = 'KO'
print(y)

x = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # [True, True, True]
y = 'KO'
if all(operator.lt(i, 10) for i in x):
    y = 'OK'
print(y)

x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # [True, True, True, False]
y = 'KO'
if all(operator.lt(i, 10) for i in x):
    y = 'OK'
print(y)

x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # [True, True, True, True]
y = 'KO'
if all(not operator.eq(i, 0) for i in x):
    y = 'OK'
print(y)
