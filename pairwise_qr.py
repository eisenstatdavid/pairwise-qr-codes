import collections
import string

from PIL import Image
from qrcodegen import *

from group_test import *
from null_space import *


version = 6
n = 134
transparent_qr_code_count = 14


def encode(data):
    code = QrCode.encode_segments(
        [QrSegment.make_bytes(data)],
        ecl=QrCode.Ecc.LOW,
        minversion=version,
        maxversion=version,
        mask=0,
        boostecl=False,
    )
    return (
        sum(
            int(code.get_module(x, y)) << (code.get_size() * y + x)
            for y in range(code.get_size())
            for x in range(code.get_size())
        ),
        code.get_size(),
    )


def E(i):
    v = bytearray(n)
    q, r = divmod(i, 8)
    v[q] ^= 1 << r
    return bytes(v)


# We can XOR a QR code by any vector spanned by the offsets and get another
# valid QR code.
origin, size = encode(b"\0" * n)
offsets = [encode(E(i))[0] ^ origin for i in range(8 * n)]
# Shuffle the offsets to avoid clumping.
random.shuffle(offsets)

# Figure out which bits are data bits and which bits are error correction bits.
diffs = collections.Counter()
for v in offsets:
    while v:
        b = v & -v
        diffs[b.bit_length() - 1] += 1
        v ^= b
data_bits = [i for (i, c) in diffs.items() if c == 1]
error_correction_bits = [i for (i, c) in diffs.items() if c > 1]

# Move the origin so that the data bits are all clear. This is really not OK
# since the resulting QR codes may be unusually sparse, but hopefully it will
# work anyway.
all_ones = 0
for i in data_bits:
    all_ones ^= 1 << i
for v in offsets:
    if (origin & all_ones) & v:
        origin ^= v

# Find "component" vectors in the offset space with pairwise disjoint support.
projections = []
for v in offsets:
    p = 0
    for j, i in enumerate(error_correction_bits):
        if v & (1 << i):
            p ^= 1 << j
    projections.append(p)
components = []
while True:
    choices = find_null(projections)
    if choices is None:
        break
    c = 0
    for i in sorted(choices, reverse=True):
        c ^= offsets[i]
        del offsets[i]
        del projections[i]
    components.append(c)

# Construct a non-adaptive group test.
test = greedy_non_adaptive_group_test(transparent_qr_code_count, 2)

# Construct the QR codes for the transparencies.
transparencies = [origin] * transparent_qr_code_count
for j, group in enumerate(test):
    for i in group:
        transparencies[i] ^= components[j]

# Validate that the combinations are all different at least. This property is
# quite permissive, but it's better than nothing.
pairs = [a | b for (a, b) in itertools.combinations(transparencies, 2)]
assert len(set(pairs)) == len(pairs)


# Output.
def write_image(name, v):
    im = Image.new("1", (size, size), 1)
    for y in range(size):
        for x in range(size):
            if v & (1 << (size * y + x)):
                im.putpixel((x, y), 0)
    im.save(name)


for letter, v in zip(string.ascii_lowercase, transparencies):
    write_image(letter + ".png", v)
for i, p in enumerate(random.sample(pairs, 10)):
    write_image("pair-%d.png" % i, p)
