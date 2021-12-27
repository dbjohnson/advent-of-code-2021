from functools import lru_cache
from collections import defaultdict
import pandas as pd
import numpy as np


with open('input.txt') as fh:
    depthmap = pd.DataFrame([{
        'row': row,
        'col': col,
        'height': int(d)
    }
        for row, line in enumerate(fh)
        for col, d in enumerate(line.strip())
    ]).pivot_table(
        index='row',
        columns='col',
        values='height'
    ).values


idx = (
    # right neighbor
    np.pad(
        depthmap[:, :-1] < depthmap[:, 1:],
        ((0, 0), (0, 1)),
        'constant',
        constant_values=1
    ) &
    # left neighbor
    np.pad(
        depthmap[:, 1:] < depthmap[:, :-1],
        ((0, 0), (1, 0)),
        'constant',
        constant_values=1
    ) &
    # lower neighbor
    np.pad(
        depthmap[:-1, :] < depthmap[1:, :],
        ((0, 1), (0, 0)),
        'constant',
        constant_values=1
    ) &
    # upper neighbor
    np.pad(
        depthmap[1:, :] < depthmap[:-1, :],
        ((1, 0), (0, 0)),
        'constant',
        constant_values=1
    )
)

print('part 1', (depthmap[np.where(idx)] + 1).sum())


# lru_cache here is essentially cheap DP - once we've calculated
# the basin for any point A, we know the basin for any point B that
# flows through point A
@lru_cache(maxsize=None)
def lowpoint(row, col):
    if depthmap[row, col] == 9:
        return None

    drains = {(row, col)}
    for r, c in (
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1)
    ):
        if (
            0 <= r < depthmap.shape[0]
            and 0 <= c < depthmap.shape[1]
            and depthmap[r, c] < depthmap[row, col]
        ):
            drains.add(lowpoint(r, c))

    return min(
        drains,
        key=lambda rowcol: depthmap[rowcol]
    )


lowpoint_to_basin = defaultdict(list)
for r in range(depthmap.shape[0]):
    for c in range(depthmap.shape[1]):
        lowpoint_to_basin[lowpoint(r, c)].append((r, c))


print(
    'part 2',
    np.prod(sorted([
        len(points)
        for basin, points in lowpoint_to_basin.items()
        if basin
    ])[-3:])
)


# part 1 now that we solved part 2...
print(
    'part 1 redux',
    sum([
        depthmap[lowpoint] + 1
        for lowpoint in lowpoint_to_basin
        if lowpoint
    ])
)