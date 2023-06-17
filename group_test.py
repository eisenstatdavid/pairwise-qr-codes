import collections
import itertools
import math


def residual_entropy(outcomes, test):
    return math.fsum(
        m * math.log2(m)
        for m in sorted(
            collections.Counter(
                tuple([outcome.isdisjoint(group) for group in test])
                for outcome in outcomes
            ).values()
        )
    ) / len(outcomes)


def greedy_non_adaptive_group_test(n, d):
    outcomes = [
        set(outcome)
        for k in range(d + 1)
        for outcome in itertools.combinations(range(n), k)
    ]
    test = []
    groups = [
        group for k in range(1, n + 1) for group in itertools.combinations(range(n), k)
    ]
    while residual_entropy(outcomes, test) > 0:
        test.append(
            min(
                groups,
                key=lambda group: residual_entropy(outcomes, test + [group]),
            )
        )
    return test


def _main():
    n = 14
    d = 2
    test = greedy_non_adaptive_group_test(n, d)
    print(test)
    print(len(test))


if __name__ == "__main__":
    _main()
