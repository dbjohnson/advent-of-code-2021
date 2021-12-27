import numpy as np
import pandas as pd


with open('input.txt') as fh:
    octomap = pd.DataFrame([{
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


class Octopus:
    def __init__(self, row, col):
        self.index = row, col
        self.neighbors = [
            (r, c)
            for r in range(
                max(0, row - 1),
                min(octomap.shape[0], row + 2)
            )
            for c in range(
                max(0, col - 1),
                min(octomap.shape[1], col + 2)
            )
            if (r, c) != (row, col)
        ]


octopi = [
    Octopus(r, c)
    for r in range(octomap.shape[0])
    for c in range(octomap.shape[1])
]


def propagate(octomap_init):
    octomap_next = octomap_init.copy()

    # First, the energy level of each octopus increases by 1.
    for o in octopi:
        octomap_next[o.index] += 1

    # Then, any octopus with an energy level greater than 9 flashes.
    # This increases the energy level of all adjacent octopuses by 1,
    # including octopuses that are diagonally adjacent.
    # If this causes an octopus to have an energy level greater than 9,
    # it also flashes.
    # This process continues as long as new octopuses keep having their energy
    # level increased beyond 9.
    # (An octopus can only flash at most once per step.)
    step_flashes = set()
    new_flashes = True
    while new_flashes:
        new_flashes = False
        for o in octopi:
            if octomap_next[o.index] > 9 and o.index not in step_flashes:
                step_flashes.add(o.index)
                new_flashes = True
                for idx in o.neighbors:
                    octomap_next[idx] += 1

    # Finally, any octopus that flashed during this step has its energy
    # level set to 0, as it used all of its energy to flash.
    for idx in step_flashes:
        octomap_next[idx] = 0

    return octomap_next, len(step_flashes)


flashes = 0
nextmap = octomap.copy()
for _ in range(100):
    nextmap, step_flashes = propagate(nextmap)
    flashes += step_flashes

print('part 1', flashes)

nextmap = octomap.copy()
step = 1
while True:
    nextmap, step_flashes = propagate(nextmap)
    if step_flashes == np.product(octomap.shape):
        print('part 2', step)
        break
    else:
        step += 1
