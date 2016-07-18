# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'

from Applications import shared


def deco1(f):
    def noname(a):
        return "{}:".format(f(a).ljust(17))
    return noname

    
def deco2(f):
    def noname(a, b):
        return "{} {}".format(f(a), b)
    return noname

    
def func(s):
    return s


NewImage = shared.Images(r"H:\201311\P.20131117.10293501.jpg")
print("\n1. Repr�sentation de l'instance 'NewImage' : {}".format(NewImage))
print("2. Type de l'instance 'NewImage' : {}".format(type(NewImage)))

# M�thode 1.
print("\nM�thode 1 :")
for k in NewImage.tags():
    print(deco2(deco1(func))(k, NewImage[k]))

# M�thode 2.
print("\nM�thode 2 :")
for k, v in NewImage.items():
    print(deco2(deco1(func))(k, v))

# M�thode 3.
print("\nM�thode 3 :")
for k, v in NewImage:
    print(deco2(deco1(func))(k, v))

print("originaldatetime" in NewImage)

print("\n0: Dimanche, 1: Lundi, 2: Mardi, etc.")
