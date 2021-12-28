dots = []
folds = []

with open('input.txt') as fh:
    for line in fh:
        if line.startswith('fold'):
            fold = line.strip().split(' ')[-1]
            dim, coord = fold.split('=')
            folds.append((dim, int(coord)))
        elif line.strip():
            dots.append([int(v) for v in line.strip().split(',')])


class Paper:
    def __init__(self, dots):
        self.dots = dots
        self.height = max(y for x, y in dots) + 1
        self.width = max(x for x, y in dots) + 1

    def fold(self, dim, coord):
        newdots = set()
        for x, y in self.dots:
            if dim == 'x' and x > coord:
                newdots.add((coord - (x - coord), y))
            elif dim == 'y' and y > coord:
                newdots.add((x, coord - (y - coord)))
            else:
                newdots.add((x, y))

        return Paper(newdots)

    def __repr__(self):
        rows = [
            [' '] * self.width
            for r in range(self.height)
        ]
        for x, y in self.dots:
            rows[y][x] = '*'
        return '\n'.join([''.join(r) for r in rows])


print(
    'part 1',
    len(Paper(dots).fold(*folds[0]).dots)
)

p = Paper(dots)
for dim, coord in folds:
    p = p.fold(dim, coord)

print('part 2:')
print(p)