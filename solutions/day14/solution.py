from functools import lru_cache
from collections import defaultdict


with open('input.txt') as fh:
    template = fh.readline().strip()
    fh.readline()

    rules = {
        tuple(pair): pair[0] + insert
        for line in fh
        for pair, insert in [line.strip().split(' -> ')]
    }


def react(chain):
    return ''.join(
        rules.get(pair, pair[0])
        for pair in zip(chain, chain[1:])
    ) + chain[-1]


# there are only a small number of pairs; cache their expansions
# at each number of cycles to avoid expanding the same nodes
# repeatedly
@lru_cache(maxsize=None)
def expand_chain(chain, cycles, recursed=False):
    if cycles:
        chain = react(chain)
        # expand each pair in the chain recursively - expanding
        # at the pair level allows effective cacheing
        elcounts = defaultdict(int)
        for pair in zip(chain, chain[1:]):
            for el, count in expand_chain(pair, cycles - 1, True).items():
                elcounts[el] += count

        if not recursed:
            # at last step, account for last chain element
            # (skipped in the base case due to sliding pair processing)
            elcounts[chain[-1]] += 1
        return dict(elcounts)
    elif recursed:
        # base case - start counting up the elements!
        # only count the first element in the leaf pair;
        # the second element will be accounted for via the
        # adjacent pair (expanded separately)
        # NOTE: must handle very last chain element separately
        return {chain[0]: 1}


elcounts = expand_chain(template, 10)

print(
    'part 1',
    max(elcounts.values()) - min(elcounts.values())
)

elcounts = expand_chain(template, 40)

print(
    'part 2',
    max(elcounts.values()) - min(elcounts.values())
)
