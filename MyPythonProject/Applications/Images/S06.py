def toto(x, i):
    return x*1000 + i


x = [("file1", 1234567890), ("file2", 1234567890), ("file3", 1234567891)]
c = Counter([itemgetter(1)(i) for i in x])
y = [key for key in sorted(list(c)) if c[key] > 1]
z1 = [(itemgetter(0)(i), itemgetter(1)(i)*1000) for i in sorted(sorted(x, key=itemgetter(0)), key=itemgetter(1)) if itemgetter(1)(i) not in y]

for key in sorted(list(c)):
    l1 = [(itemgetter(0)(i), itemgetter(1)(i)) for i in sorted(sorted(x, key=itemgetter(0)), key=itemgetter(1)) if itemgetter(1)(i) == key]  # [("file1", 1234567890), ("file2", 1234567890)]
    l2 = list(zip(*l1))  # [("file1", "file2"), (1234567890, 1234567890)]
    l3 = list(map(toto, l2[1], range(len(l2[1]))))  # [1234567890000, 1234567890001]
    z2 = list(zip(l2[0], l3))  # [("file1", 1234567890000), ("file2", 1234567890001), ("file3", 1234567890002)]
    z1 += z2

x = sorted(z1, key=itemgetter(1))
