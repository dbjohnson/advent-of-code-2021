with open('input.txt') as fh:
    instructions = [
        line.strip() for line in fh
    ]

# break full instruction sets into one for each input
digit_instructions = []
for i in instructions:
    if i.startswith('inp'):
        # start new rule set for input digit
        digit_instructions.append([i])
    else:
        digit_instructions[-1].append(i)


"""
Exhaustively scanning all 14 digit numbers is a non-starter;
let's take a look at these instructions to see if there are any
relationships to exploit:


for i in range(18):
    print(i + 1, ', '.join(sorted({d[i] for d in digit_instructions})))


1 inp w
2 mul x 0
3 add x z
4 mod x 26
5 div z 1, div z 26
6 add x -1, add x -13, add x -2, add x -7, add x -8, add x 10, add x 11, add x 12, add x 13, add x 14, add x 15
7 eql x w
8 eql x 0
9 mul y 0
10 add y 25
11 mul y x
12 add y 1
13 mul z y
14 mul y 0
15 add y w
16 add y 1, add y 12, add y 13, add y 14, add y 15, add y 2, add y 5, add y 6, add y 7, add y 8
17 mul y x
18 add z y


Okay, so really just two classes of rules, branching at instruction 5

rule class 1: step 5 = "div z 1"

                        w         x          y          z
------------------------------------------------------------
1 inp w             |  1-9
2 mul x 0           |             0
3 add x z           |             z
4 mod x 26          |            0-25
5 div z 1           |                                    z
6 add x (10-15)     |           10-35
7 eql x w           |             0
8 eql x 0           |             1
9 mul y 0           |                         0
10 add y 25         |                        25
11 mul y x          |                        25
12 add y 1          |                        26
13 mul z y          |                                   26z
14 mul y 0          |                         0
15 add y w          |                         w
16 add y 1,2,5,7,15 |                       w + 1-15
17 mul y x          |                       w + 1-15
18 add z y          |                             26z + w + 1-15 (see step 16)


class 1 rules always increase z by factor of 26
- think of this as pushing w + const onto stack of base 26 numbers


rule class 2: step 5 = "div z 26"
                        w         x        y          z
------------------------------------------------------------
1 inp w            |  1-9
2 mul x 0          |              0
3 add x z          |              z
4 mod x 26         |             0-25
5 div z 26         |                                  z//26
6 add x (-13 - -1) |            -13-24


rule class 2a: x == w  (z % 26 + const) == w
7 eql x w          |              1
8 eql x 0          |              0
9 mul y 0          |                      0
10 add y 25        |                     25
11 mul y x         |                      0
12 add y 1         |                      1
13 mul z y         |                                  z//26
14 mul y 0         |                      0
15 add y w         |                      w
16 add y (2-14)    |                   w + 2-14
17 mul y x         |                      0
18 add z y         |                                  z//26


rule class 2b: x != w  (z % 26 + const) != w
7 eql x w          |              0
8 eql x 0          |              1
9 mul y 0          |                      0
10 add y 25        |                     25
11 mul y x         |                     25
12 add y 1         |                     26
13 mul z y         |                                (z//26) * 26
14 mul y 0         |                      0
15 add y w         |                      w
16 add y (2-14)    |                   w + 2-14
17 mul y x         |                   w + 2-14
18 add z y         |                                (z//26) * 26 + w + 2-14 (see step 16)


class 2 rules:
if w == (z % 26 + const):
--> pop!
else
--> fiddle with LSB


NB: no rule output depends on any input register state other than z!

Turns out, there are 14 total rules, including 7 unconditional pushes
That means there are 7 possible pops, and they must all succeed to have the
net result yield 0.

While I deduced the rule classes, I must give credit to dphilipson for helping
me figure out where to go from there:
https://github.com/dphilipson/advent-of-code-2021/blob/master/src/days/day24.rs
"""


class DigitRule:
    def __init__(self, instructions):
        self.instructions = instructions
        if instructions[4] == "div z 1":
            self.type = 'push'
            self.const = int(instructions[15].split()[-1])
        else:
            self.type = 'pop'
            self.const = int(instructions[5].split()[-1])


rules = [
    DigitRule(instructions)
    for instructions in digit_instructions
]

stack = []
push_pop_pairs = []
for digit, rule in enumerate(rules):
    if rule.type == 'push':
        stack.insert(0, (digit, rule))
    else:
        push_pop_pairs.append((
            stack.pop(0),
            (digit, rule))
        )


def find_best_number(check_order):
    def find_best_inputs(msd_rule, lsd_rule):
        for msd in check_order:
            for lsd in check_order:
                if msd + msd_rule.const == lsd - lsd_rule.const:
                    return msd, lsd

    number = 0
    for (d1, msd_rule), (d2, lsd_rule) in push_pop_pairs:
        msd, lsd = find_best_inputs(msd_rule, lsd_rule)
        number += msd * (10 ** (len(rules) - d1 - 1))
        number += lsd * (10 ** (len(rules) - d2 - 1))
    return number


print(
    'part 1:',
    find_best_number(range(9, 0, -1))
)

print(
    'part 2:',
    find_best_number(range(1, 10))
)
