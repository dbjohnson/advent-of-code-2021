import time
import re
from queue import PriorityQueue


STEP_COST = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}


class Amphipod:
    def __init__(self, x, y, color, steps=0):
        self.x = x
        self.y = y
        self.color = color
        self.steps = steps

    def moves(self, world):
        # if we're in the hallway and there's a clear path to our room,
        # zip right over
        if (
            self.in_hallway(world)
            and self.homeroom_open(world)
            and self.path_to_homeroom_clear(world)
        ):
            yield Amphipod(
                world.homecols[self.color],
                self.y + 1,
                self.color,
                self.steps + self.homeroom_distance(world)
            )
        else:
            # otherwise, try all level combos
            def advance_if_blocking(mv):
                if mv.blocking_room(world):
                    # never stop at the exit of a room!
                    yield from mv.moves(world)
                else:
                    yield mv

            for x, y in {
                (self.x - 1, self.y),
                (self.x + 1, self.y),
                (self.x, self.y - 1),
                (self.x, self.y + 1)
            }.difference(
                # can't go anywhere there's already somebody
                {(a.x, a.y) for a in world.amphipods}
            ):
                # can't go through walls
                if world.map[y][x] != '#':
                    mv = Amphipod(x, y, self.color, self.steps + 1)
                    if self.in_hallway(world):
                        # never stop at exit!
                        if (
                            self.blocking_room(world) and (
                                mv.in_hallway(world)
                                or (
                                    self.homeroom_open(world)
                                    and mv.in_homeroom(world)
                                )
                            )
                        ):
                            yield from advance_if_blocking(mv)

                        # already moving + staying in hall
                        elif (
                            world.last_mover in (None, self)
                            and mv.in_hallway(world)
                        ):
                            yield from advance_if_blocking(mv)

                    elif (
                        not self.in_homeroom(world)
                        # only move out of our homeroom if we're blocking
                        # somebody else
                        or self.trapping_others(world)
                        # or moving farther down in the room...
                        or mv.y > self.y
                    ):
                        yield from advance_if_blocking(mv)

    def trapping_others(self, world):
        return self.in_homeroom(world) and len([
            a for a in world.amphipods
            if a.color != self.color
            and a.x == self.x
            and a.y > self.y
        ]) > 0

    def homeroom_open(self, world):
        "Make sure there are no off-color amphipods in room"
        return len([
            a for a in world.amphipods
            if a.color != self.color
            and a.x == world.homecols[self.color]
        ]) == 0

    def path_to_homeroom_clear(self, world):
        return self.in_hallway(world) and len([
            # check for amphipods in the hallway between here and home base
            a for a in world.amphipods
            if a != self
            and a.y == self.y
            and min(self.x, world.homecols[self.color]) <= a.x <= max(self.x, world.homecols[self.color])
        ]) == 0 and (
            # nobody right at the door
            (world.homecols[self.color], self.y + 1) not in
            {(a.x, a.y) for a in world.amphipods}
        )

    def blocking_room(self, world):
        return (
            self.x in world.homecols.values()
            and self.in_hallway(world)
        )

    def in_hallway(self, world):
        return world.map[self.y][self.x] == '.'

    def in_homeroom(self, world):
        return (
            self.x == world.homecols[self.color]
            and not self.in_hallway(world)
        )

    def homeroom_distance(self, world):
        steps = 0
        y = self.y
        # get into hallway
        while world.map[y][self.x] != '.':
            y -= 1
            steps += 1
        # traverse hall
        steps += abs(self.x - world.homecols[self.color])
        # drop into room
        return steps + 1


class WorldState:
    def __init__(self, cleanmap, homecols, amphipods, last_mover=None):
        self.map = cleanmap
        self.amphipods = amphipods
        self.homecols = homecols
        self.last_mover = last_mover

        self.finished = all([
            a.in_homeroom(self)
            for a in self.amphipods
        ])

        self.total_energy = sum([
            STEP_COST[a.color] * a.steps
            for a in self.amphipods
        ])

        self.estimated_total = self.total_energy + sum([
            STEP_COST[a.color] * a.homeroom_distance(self)
            for a in self.amphipods
        ])

    def from_string(string):
        rows = string.strip().split('\n')
        cleanmap = [
            list(re.sub(r'[ABCD]', ' ', row))
            for row in rows
        ]

        homecols = {
            color: match.start()
            for color, match in zip(
                'ABCD',
                re.finditer('[ABCD]', rows[-2])
            )
        }

        amphipods = [
            Amphipod(m.start(), i, m.group())
            for i, row in enumerate(rows)
            for m in re.finditer('[ABCD]', row)
        ]

        return WorldState(cleanmap, homecols, amphipods)

    @property
    def next(self):
        for i, a in enumerate(self.amphipods):
            for m in a.moves(self):
                yield WorldState(
                    self.map,
                    self.homecols,
                    self.amphipods[:i] + [m] + self.amphipods[i + 1:],
                    m
                )

    def __repr__(self):
        rows = [
            row[:] for row in self.map
        ]
        for a in self.amphipods:
            rows[a.y][a.x] = a.color

        return '\n'.join(
            ''.join(row)
            for row in rows
        )

    def __lt__(self, other):
        return self.estimated_total < other.estimated_total


def search(worldmap):
    tstart = time.time()
    visited = set()
    q = PriorityQueue()
    w = WorldState.from_string(worldmap)
    q.put(w)
    while not q.empty():
        w = q.get()
        if str(w) not in visited:
            visited.add(str(w))
            if not len(visited) % 20000:
                print(len(visited))
                print(w)
                print()
            if w.finished:
                print('solution:')
                print('nodes visited:', len(visited))
                print('minutes elapsed:', round((time.time() - tstart) / 60, 2))
                print('total energy:', w.total_energy)
                print(w)
                return w
            for child in w.next:
                q.put(child)


solution = search("""
#############
#...........#
###A#C#B#B###
  #D#D#A#C#
  #########
""")
print(
    '\npart 1:',
    solution.total_energy,
    '\n\n'
)

solution = search("""
#############
#...........#
###A#C#B#B###
  #D#C#B#A#
  #D#B#A#C#
  #D#D#A#C#
  #########
""")
print(
    '\npart 2:',
    solution.total_energy
)
