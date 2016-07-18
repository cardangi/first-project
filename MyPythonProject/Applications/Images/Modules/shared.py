# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'

import os
from pathlib import Path


def getsequencenumber(year, frm=1):
    """
    Re�oit une ann�e.
    Re�oit un num�ro de s�quence de d�part.
    Retourne le premier num�ro de s�quence disponible parmi les fichiers images respectant le masque "h:\{ann�e}{mois}\{ann�e}{mois}_{s�quence}.jpg".
    """
    for seq1 in range(frm, 100000):
        for seq2 in range(1, 13):
            if Path(os.path.join("h:\\", "{0}{1}".format(year, str(seq2).zfill(2)), "{0}{1}_{2}.jpg".format(year, str(seq2).zfill(2), str(seq1).zfill(5)))).exists():
                break
        else:
            return seq1


if __name__ == "__main__":
    print(getsequencenumber(2010))
