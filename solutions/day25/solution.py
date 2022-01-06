with open('input.txt') as fh:
    lines = [line.strip() for line in fh]

height = len(lines)
width = len(lines[0])


class SeaCuke:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction

    @property
    def fwd(self):
        x, y = self.x, self.y
        if self.direction == '>':
            x += 1
        elif self.direction == '<':
            x -= 1
        elif self.direction == '^':
            y -= 1
        elif self.direction == 'v':
            y += 1
        else:
            raise RuntimeError(self.direction)

        return SeaCuke(x % width, y % height, self.direction)

    @property
    def position(self):
        return (self.x, self.y)

    def __repr__(self):
        return self.direction

    def __hash__(self):
        return hash('|'.join([str(self.x), str(self.y), self.direction]))

    def __eq__(self, other):
        return all(
            self.x == other.x,
            self.y == other.y,
            self.direction == other.direction
        )


cukes = {
    SeaCuke(j, i, char)
    for i, line in enumerate(lines)
    for j, char in enumerate(line)
    if char != '.'
}


def step_herd(cukes, direction):
    occupied_positions = {
        c.position for c in cukes
    }

    return {
        c.fwd if c.fwd.position not in occupied_positions else c
        for c in cukes
        if c.direction == direction
    }.union({
        c for c in cukes
        if c.direction != direction
    })


def draw_herd(cukes):
    rows = [
        ['.'] * width
        for _ in range(height)
    ]

    for c in cukes:
        rows[c.y][c.x] = str(c)

    return '\n'.join([
        ''.join(row)
        for row in rows
    ])


steps = 0
while True:
    steps += 1
    next_state = step_herd(step_herd(cukes, '>'), 'v')
    if not cukes.difference(next_state):
        print('part 1:', steps)
        break
    else:
        cukes = next_state
    print(steps)
    print(draw_herd(cukes))
    print()
