with open('input.txt') as fh:
    readings = list(map(int, fh.readlines()))

# part 1
print(sum([
    curr > last
    for curr, last in zip(readings[1:], readings)
]))

# part 2
windowed = list(map(
    sum,
    zip(*[readings[i:] for i in range(3)])
))

print(sum([
    curr > last
    for curr, last in zip(windowed[1:], windowed)
]))

