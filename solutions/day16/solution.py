import numpy as np


class Packet:
    def __init__(self, bits=None, hex=None):
        self.hex = hex
        if bits:
            self.bits = bits
        else:
            self.bits = ''.join([
                '1' if (1 << bit) & int(char, 16) else '0'
                for char in hex
                for bit in reversed(range(4))
            ])

    @property
    def version(self):
        return self.bin2dec(self.bits[:3])

    @property
    def type(self):
        return self.bin2dec(self.bits[3:6])

    @property
    def length_type(self):
        if not self.is_literal:
            return self.bits[6]

    @property
    def is_literal(self):
        return self.type == 4

    @property
    def payload_start(self):
        if self.is_literal:
            return 6
        elif self.length_type == '0':
            return 22
        elif self.length_type == '1':
            return 18

    @property
    def payload(self):
        return self.bits[self.payload_start:]

    @property
    def literal(self):
        if self.is_literal:
            bits = []
            for pos in range(self.payload_start, len(self.bits), 5):
                bits.extend(self.bits[pos + 1: pos + 5])
                if self.bits[pos] == '0':
                    break
            return self.bin2dec(bits)

    @property
    def value(self):
        if self.is_literal:
            return self.literal
        else:
            return {
                0: sum,
                1: np.product,
                2: min,
                3: max,
                5: lambda vals: 1 if vals[0] > vals[1] else 0,
                6: lambda vals: 1 if vals[0] < vals[1] else 0,
                7: lambda vals: 1 if vals[0] == vals[1] else 0,
            }[self.type]([d.value for d in self.subpackets])

    @property
    def subpackets(self):
        if self.is_literal:
            return []
        elif self.length_type == '0':
            children = []
            total_bits = self.bin2dec(self.bits[7:self.payload_start])
            pos = 0
            while pos < total_bits:
                child = Packet(bits=self.payload[pos:])
                pos += child.stopbit
                children.append(child)
            return children
        elif self.length_type == '1':
            children = []
            num_subpackets = self.bin2dec(self.bits[7:self.payload_start])
            pos = 0
            for _ in range(num_subpackets):
                child = Packet(bits=self.payload[pos:])
                pos += child.stopbit
                children.append(child)
            return children

    @property
    def descendants(self):
        for child in self.subpackets:
            yield child
            for desc in child.descendants:
                yield desc

    @property
    def stopbit(self):
        if self.is_literal:
            pos = self.payload_start
            for pos in range(self.payload_start, len(self.bits), 5):
                if self.bits[pos] == '0':
                    return pos + 5
        elif self.length_type == '0':
            return self.payload_start + self.bin2dec(self.bits[7:self.payload_start])
        elif self.subpackets:
            return (
                self.payload_start
                + sum(s.stopbit for s in self.subpackets)
            )
        else:
            return len(self.bits)

    @property
    def version_sum(self):
        return self.version + sum(s.version for s in self.descendants)

    @classmethod
    def bin2dec(cls, bits):
        return sum(
            (1 << bit)
            for bit, char in enumerate(reversed(bits))
            if char == '1'
        )


with open('input.txt') as fh:
    p = Packet(hex=fh.read().strip())


print('part 1', p.version_sum)
print('part 2', p.value)
