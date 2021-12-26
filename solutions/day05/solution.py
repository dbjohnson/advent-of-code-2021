import re
from collections import defaultdict


with open('input.txt') as fh:
    lines = [[
        int(v)
        for v in re.split(
            r'[,(\s\-\>\s)]',
            line
        )
        if v
    ]
        for line in fh
    ]


def overlaps(include_diagonals=False):
    linehits = defaultdict(int)
    for x1, y1, x2, y2 in lines:
        # horizontal
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                linehits[x1, y] += 1
        # vertical
        elif y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                linehits[x, y1] += 1
        # diagonal
        elif include_diagonals:
            for step in range(abs(x2 - x1) + 1):
                linehits[
                    x1 + (step * (1 if x2 > x1 else -1)),
                    y1 + (step * (1 if y2 > y1 else -1))
                ] += 1

    return len([v for v in linehits.values() if v > 1])



print('part 1', overlaps(include_diagonals=False))
print('part 2', overlaps(include_diagonals=True))