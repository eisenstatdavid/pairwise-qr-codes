import itertools
import random


def find_null(bit_vectors):
    d = max((v.bit_length() for v in bit_vectors), default=0)
    # Truncate and transpose.
    A = [0] * d
    for j, v in enumerate(bit_vectors[: d + 1]):
        for i in range(d):
            if v & (1 << i):
                A[i] ^= 1 << j
    # Gaussian elimination.
    for j in range(d):
        pivots = (i for i in range(j, d) if A[i] & (1 << j))
        try:
            i = next(pivots)
        except StopIteration:
            d = j
            break
        A[i], A[j] = A[j], A[i]
        for i in range(d):
            if (A[i] & (1 << j)) and i != j:
                A[i] ^= A[j]
    if len(bit_vectors) <= d:
        return None
    # Solve.
    residual = 0
    choices = [d]
    for i in range(d):
        if A[i] & (1 << d):
            residual ^= 1 << i
    for j in range(d - 1, -1, -1):
        if residual & (1 << j):
            choices.append(j)
            for i in range(j + 1):
                if A[i] & (1 << j):
                    residual ^= 1 << i
    return choices if not residual else None


def _is_null(bit_vectors, choices):
    residual = 0
    for i in choices:
        residual ^= bit_vectors[i]
    return not residual


def _slow_find_null(bit_vectors):
    for k in range(1, len(bit_vectors) + 1):
        for choices in itertools.combinations(range(len(bit_vectors)), k):
            if _is_null(bit_vectors, choices):
                return choices
    return None


def _main():
    for t in range(1000000):
        bit_vectors = [random.randrange(8) for j in range(random.randrange(6))]
        fast = find_null(bit_vectors)
        slow = _slow_find_null(bit_vectors)
        assert (fast is None) == (slow is None), (bit_vectors, fast, slow)
        if fast is not None:
            assert _is_null(bit_vectors, fast), (bit_vectors, fast)


if __name__ == "__main__":
    _main()
