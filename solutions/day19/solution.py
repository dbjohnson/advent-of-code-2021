from itertools import combinations

import numpy as np
import pandas as pd
from looptimer import timedloop


class Rotator:
    def __init__(self, xrot, yrot, zrot):
        self.rot_matrix = (np.matrix([
            [1, 0, 0],
            [0, np.cos(xrot), -np.sin(xrot)],
            [0, np.sin(xrot), np.cos(xrot)],
        ]) * np.matrix([
            [np.cos(yrot), 0, np.sin(yrot)],
            [0, 1, 0],
            [-np.sin(yrot), 0, np.cos(yrot)],
        ]) * np.matrix([
            [np.cos(zrot), -np.sin(zrot), 0],
            [np.sin(zrot), np.cos(zrot), 0],
            [0, 0, 1]
        ])).round().astype(int)

    def rotate(self, matrix):
        return matrix * self.rot_matrix

    def __hash__(self):
        return hash(str(self.rot_matrix))

    def __eq__(self, other):
        return (self.rot_matrix == other.rot_matrix).all()

    def __repr__(self):
        return str(self.rot_matrix)


orientations = [
    angle * np.pi / 180
    for angle in (0, 90, 180, 270)
]

rotators = {
    Rotator(xrot, yrot, zrot)
    for xrot in orientations
    for yrot in orientations
    for zrot in orientations
}


class Cluster:
    def __init__(self, scanners):
        self.scanners = scanners
        self.name = '|'.join(sorted([s.name for s in self.scanners]))
        self.root = scanners[0]

    @property
    def beacons(self):
        return pd.DataFrame(
            np.concatenate([
                scanner.beacons
                for scanner in self.scanners
            ])
        ).drop_duplicates().values

    def num_matches(self, other):
        return self.diffs(other).max()

    def merge(self, other):
        if self.mergeable(other):
            delta = other.diffs(self).idxmax()
            return Cluster(
                list(set(self.scanners + [
                    s.translate(delta)
                    for s in other.scanners
                ]))
            )
        else:
            return self

    def mergeable(self, other):
        return self.num_matches(other) >= 12

    def diffs(self, other):
        return pd.Series([
            tuple((r1 - r2))
            for r1 in self.beacons
            for r2 in other.beacons
        ]).value_counts()

    @property
    def rotations(self):
        for r in rotators:
            yield Cluster(
                [s.rotate(r) for s in self.scanners]
            )

    @property
    def span(self):
        return max([
            np.absolute(s1.position - s2.position).sum()
            for s1, s2 in combinations(self.scanners, 2)
        ])



class Scanner:
    def __init__(self, name, beacons, position=(0, 0, 0)):
        self.name = name
        self.beacons = np.matrix(beacons)
        self.position = np.matrix(position)

    @property
    def rotations(self):
        for r in rotators:
            yield self.rotate(r)

    def rotate(self, rotator):
        return Scanner(
            self.name,
            rotator.rotate(self.beacons),
            rotator.rotate(self.position)
        )

    def translate(self, delta):
        return Scanner(
            self.name,
            self.beacons - delta,
            self.position - delta
        )

    def __hash__(self):
        return hash(
            self.name + str(self.beacons) + str(self.position)
        )

    def __eq__(self, other):
        return all([
            self.name == other.name,
            (self.beacons == other.beacons).all(),
            (self.position == other.position).all()
        ])


def load():
    with open('input.txt') as fh:
        name = None
        beacons = []
        for line in fh:
            if 'scanner' in line:
                name = line.strip()
                beacons = []
            elif line.strip():
                beacons.append([int(v) for v in line.strip().split(',')])
            else:
                yield Scanner(name, beacons)
        yield Scanner(name, beacons)


scanners = list(load())


def merge(clusters):
    merged = []
    used = set()
    for cluster in timedloop(clusters):
        if {s.name for s in cluster.scanners}.difference(used):
            used.update(cluster.scanners)
            for c2 in clusters:
                if {s.name for s in c2.scanners}.difference(used):
                    for r in c2.rotations:
                        if cluster.mergeable(r):
                            used.update({s.name for s in c2.scanners})
                            cluster = cluster.merge(r)
                            break
            merged.append(cluster)

    if len(merged) < len(clusters) and len(merged) > 1:
        # recursively merge
        return merge(merged)
    else:
        return merged


merged = merge([Cluster([s]) for s in scanners])

print(
    'part 1:',
    sum([
        len(c.beacons)
        for c in merged
    ])
)

print(
    'part 2:',
    max([
        c.span
        for c in merged
    ])
)