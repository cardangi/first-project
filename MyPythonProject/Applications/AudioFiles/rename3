# -*- coding: ISO-8859-1 -*-
from mutagen.flac import FLAC
from operator import gt
import re

__author__ = 'Xavier ROSSET'


# ==========
# Functions.
# ==========
def fixup(seq):
    if len(seq) == 1:
        return seq[0]
    return seq

	
# ================
# Initializations.
# ================
regex = re.compile(r"\W+")
tasks = list()


# ===============
# Main algorithm.
# ===============
for ifil in sorted(list_files):

    # Get a FLAC filetype instance.
    audio = FLAC(ifil)

    # Grab audio metadata.
    tags = {key.lower(): fixup(value) for key, value in audio.items()}

    # Grab source file dirname, basename and extension.
    dir, bas, ext = os.path.split(ifil), os.path.splitext(os.path.basename(ifil))

    # Build destination file.
    ofil = "{0}.{1}".format(bas, tags.get("title", ""))
    try:
        assert ifil == "{bas}{ext}".format(bas=ofil, ext=ext[1:])
    except AssertionError:
        ofil = "{bas}{ext}".format(bas=".".join(regex.split(ofil[:len(bas) + 20].rstrip())), ext=ext)
    else:
        ofil = ifil
    finally:
        tasks.append((ifil, os.path.join(dir, ofil)))

    # Update track number if multi CDs set.
    disctotal = int(tags.get("disctotal", "0"))
    discnumber = int(tags.get("discnumber", "0"))
    tracknumber = int(tags.get("tracknumber", "0"))
    if all([gt(disctotal, 1), gt(discnumber, 0), gt(tracknumber, 0)]):
        audio["tracknumber"] = "{disc}.{track:0>2d}".format(disc=discnumber, track=tracknumber)
        audio.save()


#  2. Rename files.
for src, dst in tasks:
    os.rename(src=src, dst=dst)
