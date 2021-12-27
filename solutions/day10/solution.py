import numpy as np


with open('input.txt') as fh:
    lines = [line.strip() for line in fh]

error_scores = {
    ')': 3,
    ']': 57,
    '}': 1197,
    '>': 25137
}

brackets = {
    '(': ')',
    '[': ']',
    '{': '}',
    '<': '>'
}


def closing_sequence(line):
    to_close = []
    for i, c in enumerate(line):
        if c in brackets:
            # opening bracket - append expected closing character
            # to open list
            to_close.append(brackets[c])
        elif to_close and c == to_close[-1]:
            # last open bracket closed - take off list
            to_close = to_close[:-1]
        else:
            raise RuntimeError('invalid sequence')
    return list(reversed(to_close))


def first_error(line):
    for i, c in enumerate(line):
        if c in brackets.values() and c != closing_sequence(line[:i])[0]:
            return c


errors = [
    err for line in lines
    for err in [first_error(line)]
    if err
]

print(
    'part 1',
    sum(error_scores[c] for c in errors)
)


def autocomplete_score(line):
    score = 0
    for c in closing_sequence(line):
        score *= 5
        score += {
            ')': 1,
            ']': 2,
            '}': 3,
            '>': 4
        }[c]
    return score


print(
    'part 2',
    np.median([
        autocomplete_score(line)
        for line in lines
        if not first_error(line)
    ])
)