from math import ceil
from functools import reduce
from itertools import permutations

class SnailfishNumber:
    def __init__(self, string, parent=None):
        self.parent = parent
        self.left = self.right = self.regular = None
        try:
            self.regular = int(string)
        except ValueError:
            pairs = []
            pos = 1
            while True:
                nest_level = 0
                for idx, char in enumerate(string[pos:]):
                    if nest_level == 0 and char in (',', ']'):
                        pairs.append(
                            SnailfishNumber(
                                string[pos:pos + idx],
                                self
                            )
                        )
                        pos = pos + idx + 1
                        break
                    elif char == '[':
                        nest_level += 1
                    elif char == ']':
                        nest_level -= 1
                        if nest_level == 0:
                            pairs.append(
                                SnailfishNumber(
                                    string[pos:pos + idx + 1],
                                    self
                                )
                            )
                            # skip closing bracket plus following comma
                            pos = pos + idx + 2
                            break
                else:
                    break

            assert len(pairs) == 2
            self.left, self.right = pairs

    @property
    def depth(self):
        return (self.parent.depth + 1 if self.parent else 0)

    def add_to_leftmost(self, value):
        if self.is_regular:
            self.regular += value
        else:
            self.left.add_to_leftmost(value)

    def add_to_rightmost(self, value):
        if self.is_regular:
            self.regular += value
        else:
            self.right.add_to_rightmost(value)

    @property
    def root(self):
        if self.parent:
            return self.parent.root
        else:
            return self

    def explode(self):
        if not self.is_regular and self.depth == 4:
            l, r = self.left.regular, self.right.regular
            siblings = list(self.root.children)
            idx = siblings.index(self)
            # explode left
            for sib in reversed(siblings[:idx]):
                if sib.is_regular:
                    sib.regular += l
                    break
            # explode right
            try:
                # +3 is to skip self + own l/r children
                for sib in siblings[idx + 3:]:
                    if sib.is_regular:
                        sib.regular += r
                        break
            except IndexError:
                pass

            self.left = self.right = None
            self.regular = 0
            return True

    def split(self):
        if self.is_regular and self.regular >= 10:
            self.left = SnailfishNumber(
                str(self.regular // 2),
                self
            )
            self.right = SnailfishNumber(
                str(ceil(self.regular / 2)),
                self
            )
            self.regular = None
            return True

    def reduce(self, debug=False):
        for child in self.children:
            if child.explode():
                if debug:
                    print('exploded:', str(self))
                else:
                    self.reduce()
                break
        else:
            for child in self.children:
                if child.split():
                    if debug:
                        print('split:', str(self))
                    else:
                        self.reduce()
                    break
        return self

    @property
    def children(self):
        if not self.is_regular:
            for n in [self.left, self.right]:
                yield n
                yield from n.children

    @property
    def is_regular(self):
        return self.regular is not None

    def plus(self, other):
        return SnailfishNumber(f'[{self},{other}]').reduce()

    @property
    def magnitude(self):
        if self.is_regular:
            return self.regular
        else:
            return 3 * self.left.magnitude + 2 * self.right.magnitude

    def __repr__(self):
        if self.is_regular:
            return str(self.regular)
        else:
            return f'[{self.left},{self.right}]'


with open('input.txt') as fh:
    numbers = [
        SnailfishNumber(line.strip())
        for line in fh
    ]

print(
    'part 1:',
    reduce(
        lambda l, r: l.plus(r),
        numbers
    ).magnitude
)

print(
    'part 2:',
    max([
        l.plus(r).magnitude
        for l, r in permutations(numbers, 2)
    ])
)