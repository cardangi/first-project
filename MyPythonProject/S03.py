# -*- coding: ISO-8859-1 -*-
__author__ = 'Xavier ROSSET'


# import ftplib
#
#
# session = ftplib.FTP(host="192.168.1.20", user="xavier", passwd="14Berc10", timeout=60)
# session.cwd("music")
# for fld in session.nlst():
#     if not fld.startswith("#"):
#         session.cwd(fld)
#         for i in session.nlst():
#             session.cwd(i)
#             for j in session.nlst():
#                 print("%s - %s: %s" % (fld, i, j))
#             session.cwd("..")
#         session.cwd("..")
# session.quit()

x = [
    {
        "workspace": "music",
        "target": "Artists [A-E]",
        "uid": "854796030"
    },
    {
        "workspace": "music",
        "target": "Artists [F-J]",
        "uid": "1674209532"
    },
    {
        "workspace": "music",
        "target": "Artists [K-O]",
        "uid": "1196865155"
    },
    {
        "workspace": "music",
        "target": "Artists [P-T]",
        "uid": "1535780732"
    },
    {
        "workspace": "music",
        "target": "Artists [U-Z]",
        "uid": "204959095"
    },
    {
        "workspace": "music",
        "target": "[Pearl Jam - 2000]",
        "uid": "1460302155"
    },
    {
        "workspace": "music",
        "target": "[Pearl Jam - 2003]",
        "uid": "1557918403"
    },
    {
        "workspace": "music",
        "target": "[Pearl Jam - 2006]",
        "uid": "1404261019"
    },
    {
        "workspace": "music",
        "target": "[Pearl Jam - 2010]",
        "uid": "445045058"
    },
    {
        "workspace": "music",
        "target": "[Pearl Jam - 2011]",
        "uid": "1484552884"
    }
]

# for i in x:
#     for j in i.items():
#         print(j)

print([sorted([d[key] for key in d.keys()]) for d in x])
