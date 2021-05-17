#!/usr/bin/python3

from typing import Generator, List, Tuple


class ContinuedFraction:
    def __init__(self, n: int, d: int):
        """
        Stores a fraction n/d

        :param n: int, the nominator in fraction n/d
        :param d: int, the denominator in fraction n/d
        """
        self.n = n
        self.d = d
        self.expansions: List[int] or None = None

    def expansion(self) -> List[int]:
        """
        Converts a rational fraction n/d into continued fraction expansion of
        coefficients [q0;q1,q2,q3,...,qn]
        Since n/d is rational, it has a finite continued fraction expansion.

        Generally, we use Euclidean algorithm to implement this function to
        avoid loss of precision in float calculations.

        :return: A list of the continued fraction expansion coefficients of n/d
        :rtype: List[int]
        """

        # stores the continued fraction coefficients to be returned
        e: List[int] = []

        # We reassign the values to (a, b) for iteration
        a, b = self.n, self.d

        # This is the iterative implementation of Euclidean Algorithm
        while b != 0:
            q, r = divmod(a, b)
            # the quotient will be part of the continued fraction coefficients
            e.append(q)

            # reassign (a, b) for next iteration
            a, b = b, r

        self.expansions = e
        return e

    def convergents_iter(self) -> Generator[Tuple[int, int], None, None]:
        """
        This function returns a python generator that gives you all pairs of
        convergents of the continued fraction that can be used to approximate it

        The convergents are calculated recursively using the formula
        n_i = e_i * n_{i-1} + n_{i-2}
        d_i = e_i * d_{i-1} + d_{i-2}
        in which e_i refers to elements in the expansion coefficients.

        :return: A generator that iterates over convergents of the fraction
        :rtype: Generator[Tuple[int, int], None, None]
        """

        if self.expansions is None:
            # Expansion not calculated, do that first
            self.expansion()

        e = self.expansions

        n: List[int] = []  # Nominators
        d: List[int] = []  # Denominators

        for i in range(len(e)):
            # The base cases when i = 0 or 1
            if i == 0:
                ni = e[0]
                di = 1
            elif i == 1:
                ni = e[1] * e[0] + 1
                di = e[1]
            else:
                # i > 1; use the recursive formula
                ni = e[i] * n[i - 1] + n[i - 2]
                di = e[i] * d[i - 1] + d[i - 2]

            # stores n & d for recursive use later
            n.append(ni)
            d.append(di)

            yield ni, di
