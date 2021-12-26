from itertools import permutations

segments_to_digit = {
    'abcefg': 0,
    'cf': 1,
    'acdeg': 2,
    'acdfg': 3,
    'bcdf': 4,
    'abdfg': 5,
    'abdefg': 6,
    'acf': 7,
    'abcdefg': 8,
    'abcdfg': 9
}

translations = [
    str.maketrans(''.join(p), 'abcdefg')
    for p in permutations('abcdefg', 7)
]


def descramble(patterns, outputs):
    for trans in translations:
        translator = {
            ''.join(sorted(p)): ''.join(sorted(p.translate(trans)))
            for p in patterns
        }
        if set(translator.values()) == set(segments_to_digit.keys()):
            return int(''.join([
               str(segments_to_digit[translator[''.join(sorted(o))]])
               for o in outputs
            ]))


with open('input.txt') as fh:
    lines = fh.readlines()
    patterns = [line.split(' | ')[0].split(' ') for line in lines]
    outputs = [line.split(' | ')[1].strip().split(' ') for line in lines]


print(
    'part 1',
    len([
        digit
        for p, o in zip(patterns, outputs)
        for digit in str(descramble(p, o))
        if digit in '1478'
    ])
)

print(
    'part 2',
    sum(
        descramble(p, o)
        for p, o in zip(patterns, outputs)
    )
)
