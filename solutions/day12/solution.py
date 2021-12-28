class Cave:
    def __init__(self, name):
        self.name = name
        self.neighbors = set()

    def add_neighbor(self, neighbor):
        self.neighbors.add(neighbor)

    @property
    def type(self):
        if self.name in ('start', 'end'):
            return self.name
        elif self.name == self.name.upper():
            return 'big'
        else:
            return 'small'

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name


caves = dict()


with open('input.txt') as fh:
    for line in fh:
        a, b = line.strip().split('-')
        for name in (a, b):
            if name not in caves:
                caves[name] = Cave(name)

        caves[a].add_neighbor(caves[b])
        caves[b].add_neighbor(caves[a])


class Path:
    def __init__(self, steps=[caves['start']], part2=False):
        self.steps = steps
        self.part2 = part2

    @property
    def valid(self):
        small_steps = [c.name for c in self.steps if c.type == 'small']
        return all([
            # must begin at the start
            self.stepnames[0] == 'start',
            # must not visit any small cave more than once
            # EDIT - unless it's part 2, then we can visit one twice!!
            len(set(small_steps)) >= len(small_steps) - (1 if self.part2 else 0),
            # end can only be the last step
            'end' not in self.stepnames[:-1],
            # can't visit start or end more than once
            not any([
                self.stepnames.count(s) > 1
                for s in ('start', 'end')
            ])
        ])

    @property
    def stepnames(self):
        return [c.name for c in self.steps]

    @property
    def complete(self):
        return (
            self.steps[0].type == 'start'
            and self.steps[-1].type == 'end'
        )

    @property
    def children(self):
        if self.valid and not self.complete:
            for c in self.steps[-1].neighbors:
                yield Path(self.steps + [c], self.part2)

    def __hash__(self):
        return hash('|'.join(self.stepnames))

    def __repr__(self):
        return '>'.join(self.stepnames)


def find_complete_paths(part2=False):
    # we are exploring all paths, so can just use set rather
    # than using FIFO/queue (BFS), LIFO stack (DFS), or priority queue (best first)
    open_paths = set([Path([caves['start']], part2)])
    explored_paths = set(open_paths)
    complete_paths = set()
    while open_paths:
        p = open_paths.pop()
        if p.complete:
            complete_paths.add(p)

        for child in p.children:
            if child not in explored_paths:
                explored_paths.add(child)
                open_paths.add(child)

    return complete_paths


print('part 1', len(find_complete_paths()))
print('part 2', len(find_complete_paths(part2=True)))