import unittest
from genetic.Elitism import KeepBest


class TestElitism(unittest.TestCase):

    def test_KeepBestError(self):
        tests = [1.1, -0.1]

        for percent in tests:
            with self.assertRaises(ValueError, msg=f"Testing Percent: {percent}"):
                KeepBest([], [], percent)

    def test_KeepBest(self):
        tests = [([(1, 1, 1), (2, 2, 2)], [1, 1], 0.5, True, [1, 2]),
                 ([(1, 1, 1), (2, 2, 2)], [2, 2], 0.5, True, [2, 2]),
                 ([(1, 1, 1), (2, 2, 2)], [1, 1], 0.5, False, [1, 1]),
                 ([(1, 1, 1), (2, 2, 2)], [2, 2], 0.5, False, [1, 2]),
                 ([(1, 1, 1), (2, 2, 2)], [7, 7], 0, False, [7, 7]),
                 ([(1, 1, 1), (2, 2, 2)], [7, 7], 0, True, [7, 7]),
                 ([(1, 1, 1), (2, 2, 2)], [7, 7], 0.5, False, [1, 7]),
                 ([(1, 1, 1), (2, 2, 2)], [7, 7], 0.5, True, [2, 7]),
                 ([(1, 1, 1), (2, 2, 2), (3, 3, 3)], [7, 7], 1, True, [3, 2]),
                 ([(1, 1, 1), (2, 2, 2), (3, 3, 3)], [7, 7], 1, False, [1, 2])]

        for ranked, newGen, percent, rankingDirection, result in tests:
            with self.subTest():
                self.assertListEqual(sorted(KeepBest(ranked, newGen, percent, rankingDirection)), sorted(result))


if __name__ == '__main__':
    unittest.main()
