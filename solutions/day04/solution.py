import pandas as pd


with open('input.txt') as fh:
    lines = fh.readlines()


class Board(object):
    def __init__(self, lines):
        self.values = [
            (int(val), r, c)
            for r, row in enumerate(lines)
            for c, val in enumerate(row.split())
        ]
        self.board = pd.DataFrame([[0] * 5] * 5)
        self.last_num = 0

    def update(self, number):
        for val, r, c in self.values:
            if val == number:
                self.board.iloc[r, c] = 1
                self.last_num = number

        self.values = [
            x for x in self.values if x[0] != number
        ]

    @property
    def score(self):
        return self.last_num * sum([x[0] for x in self.values])

    @property
    def winner(self):
        return any([
            self.board.all().any(),
            self.board.all(axis=1).any()
        ])


sequence = list(map(int, lines[0].split(',')))
boards = [
    Board(lines[offs:offs + 5])
    for offs in range(2, len(lines) + 1, 6)
]


# part 1
def find_first_winner(sequence, boards):
    for num in sequence:
        for i, b in enumerate(boards):
            b.update(num)
            if b.winner:
                return(i + 1, b.score)


print('first winner:', find_first_winner(sequence, boards))


# part 2
def find_last_winner(sequence, boards):
    for num in sequence:
        for i, b in enumerate(boards):
            if not b.winner:
                b.update(num)
                if b.winner:
                    if all([board.winner for board in boards]):
                        return (i + 1, b.score)


print('last winner:', find_last_winner(sequence, boards))