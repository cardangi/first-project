# -*- coding: ISO-8859-1 -*-
from Applications import shared

__author__ = 'Xavier ROSSET'


try:
    # myimg = shared.Images(r"H:\201601\201701_00001.JPG")
    myimg = shared.Images(r"H:\201601\201601_00001.JPG")
    # myimg = shared.Images(r"C:\Users\Xavier\Documents\toto.txt")
except shared.ExifError as e:
    print('{1} "{0}".'.format(e.file, e.error))
except (FileNotFoundError, OSError) as e:
    print(e.args[0])
else:
    print(myimg.originaldatetime)
    print(myimg)
