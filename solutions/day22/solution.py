import numpy as np
from looptimer import timedloop


with open('input.txt') as fh:
    instructions = [
        line.strip()
        for line in fh
    ]


class Cube:
    def __init__(self, dims, state=None):
        self.dims = dims
        self.state = state

    def intersect(self, other):
        intersection = [
            [max(d1[0], d2[0]), min(d1[1], d2[1])]
            for d1, d2 in zip(self.dims, other.dims)
        ]
        if all([d[0] < d[1] for d in intersection]):
            return Cube(intersection, self.state)

    def difference(self, other):
        if not self.intersect(other):
            # no intersection - difference is just self
            return [self]
        else:
            # 2 step decimation - will yield from 3 to 6 decimated cubes
            # TODO: generalize!!
            # step 1) 1-4 cubes cut through face 1, depending on intersection
            diffs = []
            d, o = self.dims, other.dims

            dim_intersect = [
                (max(d1[0], d2[0]), min(d1[1], d2[1]))
                for d1, d2 in zip(self.dims, other.dims)
            ]

            # cube 1: face 1, to left of intersection
            if d[0][0] < o[0][0]:
                diffs.append(Cube([
                    (d[0][0], o[0][0]),
                    d[1],
                    d[2]
                ], self.state))
            # cube 2: face 1, to right side of intersection
            if d[0][1] > o[0][1]:
                diffs.append(Cube([
                    (o[0][1], d[0][1]),
                    d[1],
                    d[2]
                ], self.state))
            # cube 3: face 1 below dim_intersect
            if d[1][0] < o[1][0]:
                diffs.append(Cube([
                    dim_intersect[0],
                    (d[1][0], o[1][0]),
                    d[2]
                ], self.state))

            # cube 4: face 1 above dim_intersect
            if d[1][1] > o[1][1]:
                diffs.append(Cube([
                    dim_intersect[0],
                    (o[1][1], d[1][1]),
                    d[2]
                ], self.state))

            # step 2) 0-2 cubes cut through face 2 (rotate cube 90deg about z))
            # cube 5: face 2 left of intersection
            if d[2][0] < o[2][0]:
                diffs.append(Cube([
                    dim_intersect[0],
                    dim_intersect[1],
                    (d[2][0], o[2][0]),
                ], self.state))

            # cube 6: face 2 righ of intersection
            if d[2][1] > o[2][1]:
                diffs.append(Cube([
                    dim_intersect[0],
                    dim_intersect[1],
                    (o[2][1], d[2][1]),
                ], self.state))

            diff_volume = sum(d.volume for d in diffs)
            double_check = self.volume - self.intersect(other).volume
            assert diff_volume == double_check
            assert not any([d.intersect(other) for d in diffs])
            return diffs

    @property
    def volume(self):
        return np.product([
            d[1] - d[0]
            for d in self.dims
        ])

    def __repr__(self):
        return str(self.dims)

    def __hash__(self):
        return hash(str(self.dims))

    def __eq__(self, other):
        return self.dims == other.dims


class Reactor:
    def __init__(self, init_sequence, maxdim=None):
        self.cubes = []
        for instruction in init_sequence:
            directive, dims = instruction.split(' ')

            def cap(val):
                if maxdim:
                    return max(-maxdim, min(val, maxdim))
                else:
                    return val

            cube = Cube([
                # instruction ranges are inclusive
                (cap(int(mn)), cap(int(mx) + 1))
                for dim in dims.split(',')
                for mn, mx in [dim.split('=')[-1].split('..')]
            ], directive)

            if cube.volume > 0:
                self.cubes.append(cube)

    @property
    def num_cubes_on(self):
        on_cubes = []

        def parts_not_lit(new_cubes, already_lit):
            for i, lit in enumerate(already_lit):
                for j, c in enumerate(new_cubes):
                    if c.intersect(lit):
                        # hit - replace this cube with its decimated
                        # difference, then recurse
                        return parts_not_lit(
                            new_cubes[:j] + c.difference(lit) + new_cubes[j + 1:],
                            # don't need to check against already scanned lit
                            # cubes - everything in the list at this point
                            # has alreay cleared these
                            already_lit[i:]
                        )

            # made it all the way through with no collisions!
            return new_cubes

        for c in timedloop(self.cubes):
            if c.state == 'on':
                # break new cube up into smaller cubes that don't overlap
                # existing lit areas
                on_cubes.extend(parts_not_lit([c], on_cubes))
            else:
                # turn off any lit regions as necessary via diff / split
                on_cubes = [
                    diff
                    for c2 in on_cubes
                    for diff in c2.difference(c)
                ]

        return sum([o.volume for o in on_cubes])


print(
    'part 1:',
    Reactor(instructions, 50).num_cubes_on
)

print(
    'part 2:',
    Reactor(instructions).num_cubes_on
)
