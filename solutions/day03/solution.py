import pandas as pd


with open('input.txt') as fh:
    df = pd.DataFrame([{
        i: int(v)
        for i, v in enumerate(row.strip())
    }
        for row in fh.readlines()
    ])

# part 1
gamma = df.mode().max()
epsilon = 1 - gamma


def bin2dec(vals):
    return sum([
        i << digit
        for digit, i in enumerate(reversed(vals))
    ])


print('gamma:', bin2dec(gamma))
print('epsilon:', bin2dec(epsilon))
print('product:', bin2dec(gamma) * bin2dec(epsilon))


# part 2
def filter(most_common=True):
    filtered = df.copy()
    for bit in filtered.columns:
        mode = filtered[bit].mode().max()
        filtered = filtered[
            filtered[bit] == (mode if most_common else 1 - mode)
        ]
        if len(filtered) == 1:
            return bin2dec(filtered.iloc[0])


oxygen = filter(True)
co2 = filter(False)
print('oxygen:', oxygen)
print('co2:', co2)
print('product:', oxygen * co2)