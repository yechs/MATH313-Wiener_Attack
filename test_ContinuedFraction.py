import unittest

from ContinuedFraction import ContinuedFraction


class TestContinuedFraction(unittest.TestCase):
    def test_expansion(self):
        cf = ContinuedFraction(40009, 98407)
        self.assertEqual(cf.expansion(),
                         [0, 2, 2, 5, 1, 2, 4, 6, 2, 18])

    def test_convergents_iter(self):
        cf = ContinuedFraction(40009, 98407)
        self.assertEqual(list(cf.convergents_iter()),
                         [(0, 1), (1, 2), (2, 5), (11, 27), (13, 32), (37, 91),
                          (161, 396), (1003, 2467), (2167, 5330),
                          (40009, 98407)])


if __name__ == '__main__':
    unittest.main()
