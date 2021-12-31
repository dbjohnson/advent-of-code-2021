import numpy as np

# target area: x=287..309, y=-76..-48
target = ((287, 309), (-76, -48))


class Point:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity

    def step(self):
        return Point(
            tuple([
                p + v
                for p, v in zip(self.position, self.velocity)
            ]),
            tuple([
                self.velocity[0] - 1 * np.sign(self.velocity[0]),
                self.velocity[1] - 1
            ])
        )

    @property
    def in_target_box(self):
        return self.in_target_x and self.in_target_y

    @property
    def past_target_box(self):
        return self.too_far_x or self.too_far_y

    @property
    def in_target_x(self):
        return min(target[0]) <= self.position[0] <= max(target[0])

    @property
    def in_target_y(self):
        return min(target[1]) <= self.position[1] <= max(target[1])

    @property
    def too_far_x(self):
        return self.position[0] > max(target[0])

    @property
    def too_far_y(self):
        return self.position[1] < min(target[1])

    @property
    def finished(self):
        return (
            self.in_target_box
            or self.past_target_box
            # out of gas before reaching x
            or (self.velocity[0] == 0 and self.position[0] < min(target[0]))
        )


class Trajectory:
    def __init__(self, init_velocity):
        self.points = [
            Point((0, 0), init_velocity)
        ]
        while not self.points[-1].finished:
            self.points.append(self.points[-1].step())

    @property
    def reachable_x(self):
        p = self.points[0]
        while not p.too_far_x and p.velocity[0] != 0:
            if p.in_target_x:
                return True
            p = p.step()
        return False

    @property
    def reachable_y(self):
        p = self.points[0]
        while not p.too_far_y:
            if p.in_target_y:
                return True
            p = p.step()
        return False

    @property
    def hit(self):
        return any([p.in_target_box for p in self.points])

    @property
    def ymax(self):
        return max(p.position[1] for p in self.points)

    def __repr__(self):
        height = self.ymax - min(target[1]) + 1
        scene = [
            [' '] * max(target[0])
            for _ in range(height)
        ]
        for x in range(*target[0]):
            for y in range(*target[1]):
                scene[self.ymax - y][x] = 'T'

        for point in self.points:
            try:
                scene[self.ymax - point.position[1]][point.position[0]] = '#'
            except IndexError:
                # don't worry about points out of bounds
                pass

        return '\n'.join([''.join(row) for row in scene])


# first determine valid single axis starting velocities
valid_xvels = [
    xvel for xvel in range(max(target[0]) + 1)
    if Trajectory((xvel, 0)).reachable_x
]

yvelmax = 1000
valid_yvels = [
    yvel for yvel in range(
        min(target[1]),
        # in lieu of some more prinicipled way of coming up with the
        # max y velocity limit, assume it is no higher than the
        # total distance to the end of the target range
        -min(target[1])
    )
    if Trajectory((0, yvel)).reachable_y
]

# now try all combos of single axis velocities
hits = [
    t
    for xvel in valid_xvels
    for yvel in valid_yvels
    for t in [Trajectory((xvel, yvel))]
    if t.hit
]

print(
    'part 1',
    max([t.ymax for t in hits])
)

print(
    'part 2',
    len({t.points[0].velocity for t in hits})
)