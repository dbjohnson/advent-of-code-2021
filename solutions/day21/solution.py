from functools import lru_cache

# Player 1 starting position: 4
# Player 2 starting position: 1


class Player:
    def __init__(self, position, score=0):
        self.position = position
        self.score = score

    def advance(self, steps):
        position = self.position + steps
        position = (position % 10) or 10
        score = self.score + position
        return Player(position, score)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return (
            self.position == other.position
            and self.score == other.score
        )

    def __repr__(self):
        return f'{self.position}|{self.score}'


def game(p1, p2):
    die = 0
    rolls = 0

    def roll(die):
        rolls = [(die + i) % 100 or 100 for i in range(1, 4)]
        return sum(rolls), rolls[-1]


    while True:
        rolls += 3
        total, die = roll(die)
        p1 = p1.advance(total)
        if p1.score >= 1000:
            break

        rolls += 3
        total, die = roll(die)
        p2 = p2.advance(total)
        if p2.score >= 1000:
            break

    return min(p1.score, p2.score) * rolls

print(
    'part 1:',
    game(Player(4), Player(1))
)


@lru_cache(maxsize=None)
def dirac_game(p1, p2):
    p1wins = p2wins = 0
    rolls = [
        sum([r1, r2, r3])
        for r1 in (1, 2, 3)
        for r2 in (1, 2, 3)
        for r3 in (1, 2, 3)
    ]
    for roll1 in rolls:
        if p1.advance(roll1).score >= 21:
            # player 1 wins - abort recursion for player 2 rolls
            p1wins += 1
        else:
            for roll2 in rolls:
                if p2.advance(roll2).score >= 21:
                    p2wins += 1
                else:
                    p1w, p2w = dirac_game(p1.advance(roll1), p2.advance(roll2))
                    p1wins += p1w
                    p2wins += p2w

    return p1wins, p2wins


print(
    'part 2:',
    max(dirac_game(Player(4), Player(1)))
)