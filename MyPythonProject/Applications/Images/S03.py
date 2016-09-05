from operator import itemgetter
from functools import partial
from shutil import copytree
import os


# ==========
# Functions.
# ==========
def graboriginalmonth(s, rex):
    return s, rex.match(s)


# ========
# Classes.
# ========
class IgnoreBut(object):

    def __init__(self, *patterns):
        self._patterns = patterns

    def __call__(self, path, content):
        l = list()
        for item in content:
            for pattern in self._patterns:
                match = re.match(pattern, item)
                if match:
                    break
            else:
                l.append(item)
        return l


# ==================
# Initializations 1.
# ==================
src = r"G:\Computing\Vidéos\Samsung S5"
graboriginalmonth = partial(graboriginalmonth, rex=re.compile(r"^({0}{1}){2}\B_\B[^\.]+\.jpg$".format(shared.DFTREGEXYEAR, shared.DFTREGEXMONTH, shared.DFTREGEXDAY), re.IGNORECASE))


# ===============
# Main algorithm.
# ===============
reflist = [(fil, obj.group(1)) for fil, obj in map(graboriginalmonth, list(filesinfolder(src)) if obj]
for month in set([itemgetter(1)(item) for item in reflist]):
    dst = os.path.join(r"H:\\", month)
    if not os.path.exists(dst):
        copytree(src, dst, ignore=IgnoreBut(r"^{0}{1}\B_\B[^\.]+\.jpg$".format(month, shared.DFTREGEXDAY)))
        wihg chgcurdir(dst):
            for file in os.listdir(dst):
                os.rename(file, dateutil.parse(file).timestamp())
