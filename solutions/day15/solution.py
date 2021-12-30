from queue import PriorityQueue
from collections import defaultdict
from copy import deepcopy

import numpy as np


with open('input.txt') as fh:
    risk_map = [
        [int(c) for c in row.strip()]
        for row in fh
    ]


def find_path(risk_map):
    map_height = len(risk_map)
    map_width = len(risk_map[0])
    cost_map = defaultdict(lambda: 1e12)
    start = 0, 0
    goal = map_width - 1, map_height - 1

    class Path:
        def __init__(self, steps=[start], cost_so_far=0):
            self.steps = steps
            self.x, self.y = steps[-1]
            self.cost_so_far = cost_so_far
            # city block distance, minimal risk at each step
            self.heuristic_to_go = (
                abs(self.x - goal[0]) +
                abs(self.y - goal[1])
            )
            self.total_risk_estimate = self.cost_so_far + self.heuristic_to_go

        @property
        def complete(self):
            return (self.x, self.y) == goal

        @property
        def expand(self):
            for x, y in (
                (self.x - 1, self.y),
                (self.x + 1, self.y),
                (self.x, self.y - 1),
                (self.x, self.y + 1)
            ):
                if 0 <= x < map_width and 0 <= y < map_height:
                    yield Path(
                        self.steps + [(x, y)],
                        self.cost_so_far + risk_map[y][x]
                    )

        def __lt__(self, other):
            return self.total_risk_estimate < other.total_risk_estimate

        def __repr__(self):
            m = deepcopy(risk_map)
            for x, y in self.steps:
                m[y][x] = '\033[96m' + str(m[y][x]) + '\033[0m'
            return '\n'.join(
                ''.join(str(v) for v in row)
                for row in m
            )

    q = PriorityQueue()
    p = Path()
    q.put((p.total_risk_estimate, p))
    cost_map[0, 0] = p.cost_so_far
    while q.not_empty:
        _, p = q.get()
        if p.complete:
            return p
        # only expand if we haven't found a better route to this position
        if p.cost_so_far == cost_map[(p.x, p.y)]:
            for child in p.expand:
                # only put children on the queue if best available route to loc
                if child.cost_so_far < cost_map[(child.x, child.y)]:
                    cost_map[(child.x, child.y)] = child.cost_so_far
                    q.put((child.total_risk_estimate, child))


path = find_path(risk_map)
print(
    'part 1',
    path.total_risk_estimate
)

expanded_risk_map = np.concatenate([
    np.concatenate([
        np.array(risk_map) + xtile
        for xtile in range(5)
    ], axis=1) + ytile
    for ytile in range(5)
], axis=0)

# wrap scores
expanded_risk_map -= 1
expanded_risk_map %= 9
expanded_risk_map += 1

path = find_path(expanded_risk_map.tolist())
print(
    'part 2',
    path.total_risk_estimate
)
