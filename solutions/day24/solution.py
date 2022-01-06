"""
General recursive solution; takes several minutes to run - and a pretty
hefy helping of RAM - but requires no mental gymanstics, analysis of the
instruction set, or anything else too clever.  Also actually implements
the ALU!
"""
from collections import defaultdict
from looptimer import timedloop


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


class ALU:
    def __init__(self, w=0, x=0, y=0, z=0):
        self.registers = {
            'w': w,
            'x': x,
            'y': y,
            'z': z
        }

    def run_program(self, instructions, inputs):
        input_idx = 0
        for ins in instructions:
            if ins.startswith('inp'):
                self.registers[ins.split()[-1]] = inputs[input_idx]
                input_idx += 1
            else:
                operator, target, value = ins.split()
                if value in self.registers:
                    value = self.registers[value]
                else:
                    value = int(value)

                if operator == 'add':
                    self.registers[target] += value
                elif operator == 'mul':
                    self.registers[target] *= value
                elif operator == 'div':
                    self.registers[target] //= value
                elif operator == 'mod':
                    self.registers[target] %= value
                elif operator == 'eql':
                    self.registers[target] = 1 if self.registers[target] == value else 0
                else:
                    raise RuntimeError('Unknown operator:', operator)

        return tuple(self.registers[k] for k in 'wxyz')


def assemble_digits(digits):
    return sum([
        i * 10 ** (len(digit_instructions) - 1 - d)
        for d, i in enumerate(digits)
    ])


# expand each digit into all its possible register output states, propagating
# forward only the unique set of possible output states

def propagate_unique_register_states(digit, register_states):
    instructions = digit_instructions[digit]

    if digit == len(digit_instructions) - 1:
        # last digit to check - find final states with register z set to 0
        return [
            ([i], rs)
            for i in range(1, 10)
            for rs in register_states
            if ALU(*rs).run_program(instructions, [i])[-1] == 0
        ]
    else:
        # find unique set of register state expansions given unique
        # input states and possible digits
        next_states = defaultdict(set)
        for rs in timedloop(register_states, 'checking digit ' + str(digit + 1)):
            for i in range(1, 10):
                next_rs = ALU(*rs).run_program(instructions, [i])
                next_states[next_rs].add((i, rs))

        # recurse to the next digit
        return [
            # return the assembled digits on final exit
            assemble_digits([i] + downstream_digits)
            if digit == 0
            else ([i] + downstream_digits, input_rs)
            for downstream_digits, valid_next_rs in propagate_unique_register_states(digit + 1, next_states)
            # on the return trip back up from the recursion, fan back out
            # to the digit + input register states that mapped to a successful
            # end state
            for (i, input_rs) in next_states[valid_next_rs]
        ]


valid_serials = propagate_unique_register_states(0, {(0, 0, 0, 0)})

print('part 1:', max(valid_serials))
print('part 2:', min(valid_serials))
