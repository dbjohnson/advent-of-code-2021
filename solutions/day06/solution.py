from functools import lru_cache


with open('input.txt') as fh:
    fishies = [
        int(v)
        for line in fh.readlines()
        for v in line.strip().split(',')
    ]


# cache the propagation function since there are only 8
# unique timer values x 256 days, so 8*256=2048 unique values
# to calculate; this allows us to efficiently simulate expontential
# growth invariant to the initial population size e.g., O(1)
# without significant memory usage
@lru_cache(maxsize=None)
def propagate(timer, days):
    return sum([
        propagate(8, days - d)
        # enumerate days starting from the
        # next spawn date, then regularly thereafter
        for d in range(timer + 1, days + 1, 7)
    ]) + 1  # + 1 is for the progenitor


print(
    'part 1',
    sum([
        propagate(t, 80)
        for t in fishies
    ])
)

print(
    'part 2',
    sum([
        propagate(t, 256)
        for t in fishies
    ])
)
