class Image:
    def __init__(self, rows, lut, border='.'):
        self.rows = rows
        self.lut = lut
        self.height = len(rows)
        self.width = len(rows[0])
        self.border = border

    @staticmethod
    def from_file(filename):
        with open(filename) as fh:
            lines = [line.strip() for line in fh]
            lut, rows = lines[0], lines[2:]
            return Image(rows, lut)

    def pad(self, padding=1):
        padline = self.border * (self.width + 2)
        im = Image(
            [padline] + [
                f'{self.border}{r}{self.border}'
                for r in self.rows
            ] + [padline],
            self.lut,
            self.border
        )
        if padding <= 1:
            return im
        else:
            return im.pad(padding - 1)

    def enhance(self):
        def pixel_lookup(i, j):
            lut_index = 0
            for ioffs in range(i - 1, i + 2):
                for joffs in range(j - 1, j + 2):
                    lut_index <<= 1
                    try:
                        if self.rows[ioffs + 1][joffs + 1] == '#':
                            lut_index += 1
                    except IndexError:
                        if self.border == '#':
                            lut_index += 1
            return self.lut[lut_index]

        enhanced_rows = [
            ''.join([
                pixel_lookup(i, j)
                for j in range(self.width)
            ])
            for i in range(self.height)
        ]

        # if the outer two rings only contain the default
        # background ("expanse value"), then subsequent rings
        # will also "enhance" to background
        # otherwise, must continue padding until stability
        # is reached
        expanse_value = self.lut[
            # if border is '.', then all background pixels
            # will evaluate to lut index 0; otherwise 255 (-1)
            0 if self.border == '.' else -1
        ]
        boundary_values = {
            c
            for row in (0, 1, -2, -1)
            for c in enhanced_rows[row]
        }.union({
            row[col]
            for row in enhanced_rows
            for col in (0, 1, -2, -1)
        })

        if boundary_values == {expanse_value}:
            return Image(
                enhanced_rows,
                self.lut,
                expanse_value
            )
        else:
            return self.pad().enhance()

    @property
    def lit_pixels(self):
        return str(self).count('#')

    def __repr__(self):
        return '\n'.join(self.rows)


im = Image.from_file('input.txt')
print(
    'part 1:',
    im.enhance().enhance().lit_pixels
)

for _ in range(50):
    im = im.enhance()

print(
    'part 2:',
    im.lit_pixels
)