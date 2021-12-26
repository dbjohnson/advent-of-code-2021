with open('input.txt') as fh:
    commands = [{
        'direction': line.split(' ')[0],
        'distance': int(line.split(' ')[1])
    }
        for line in fh.readlines()
    ]

# part 1
fwd = depth = 0
for c in commands:
    if c['direction'] == 'forward':
        fwd += c['distance']
    elif c['direction'] == 'down':
        depth += c['distance']
    elif c['direction'] == 'up':
        depth -= c['distance']
    else:
        raise RuntimeError(c)

print(f'fwd: {fwd}')
print(f'depth: {depth}')
print(f'product: {fwd * depth}')


# part 2
aim = fwd = depth = 0
for c in commands:
    if c['direction'] == 'forward':
        depth += c['distance'] * aim
        fwd += c['distance']
    elif c['direction'] == 'down':
        aim += c['distance']
    elif c['direction'] == 'up':
        aim -= c['distance']
    else:
        raise RuntimeError(c)

print(f'fwd: {fwd}')
print(f'depth: {depth}')
print(f'product: {fwd * depth}')