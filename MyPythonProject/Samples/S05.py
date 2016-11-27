# -*- coding: utf-8 -*-
from Applications.AudioCD.shared import getmetadata
import argparse

__author__ = 'Xavier ROSSET'


# r"F:\S\Springsteen, Bruce\2\2016\09.11 - Pittsburgh, PA\CD3\1.Free Lossless Audio Codec\2.20160911.1.13.D3.T01.flac"
# r"F:\M\Megadeth\1986 - Peace Sells...But Who's Buying_\1.Monkey's Audio\1.19860000.1.12.D1.T01.ape"
parser = argparse.ArgumentParser()
parser.add_argument("file")
arguments = parser.parse_args()

result = getmetadata(arguments.file)
print(result.found)
print(result.tags)
