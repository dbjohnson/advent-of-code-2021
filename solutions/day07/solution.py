from functools import lru_cache
import pandas as pd


positions = pd.read_csv('input.txt', header=None).T[0]


def distances(p):
    return (positions - p).abs()


best = min(
    list(range(positions.min(), positions.max() + 1)),
    key=lambda p: distances(p).sum()
)
print('part 1', distances(best).sum())


@lru_cache(maxsize=None)
def fuel_for_dist(dist):
    return sum(list(range(1, dist + 1)))


best = min(
    list(range(positions.min(), positions.max() + 1)),
    key=lambda p: distances(p).map(fuel_for_dist).sum()
)
print('part 2', distances(best).map(fuel_for_dist).sum())