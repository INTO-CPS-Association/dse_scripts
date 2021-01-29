import unittest

from genetic.Ranking import FitnessBasedRanking, NormalisedRanking, ReverseRanking


class TestRanking(unittest.TestCase):
    def setUp(self):
        self.testData = [{0: 0}, {0: 0.01}, {0: 0.99}, {0: 0.98}, {0: 0.97}, {0: 0.96}]
        self.rawRankedData = FitnessBasedRanking(self.testData, lambda x: x[0])
        self.normalRankedData = NormalisedRanking(self.rawRankedData, True)

    def test_RawRanking(self):
        result = self.rawRankedData
        self.assertListEqual([(round(f1, 3), round(f2, 3)) for _, f1, f2 in result], [(0.0, 0.0), (0.01, 0.01), (0.99, 0.99), (0.98, 0.98), (0.97, 0.97), (0.96, 0.96)])

    def test_NormalizedRankingMaximise(self):
        result = NormalisedRanking(self.rawRankedData, True)
        self.assertListEqual([(v, r) for v, r, _ in result], sorted([({0: 0}, 5), ({0: 0.01}, 4), ({0: 0.99}, 0), ({0: 0.98}, 1), ({0: 0.97}, 2), ({0: 0.96}, 3)], key=lambda x: x[1]))

    def test_NormalizedMinimise(self):
        result = NormalisedRanking(self.rawRankedData, False)
        self.assertListEqual([(v, r) for v, r, _ in result], sorted([({0: 0}, 0), ({0: 0.01}, 1), ({0: 0.99}, 5), ({0: 0.98}, 4), ({0: 0.97}, 3), ({0: 0.96}, 2)], key=lambda x: x[1]))

    def test_ReverseRankingRaw(self):
        expected = [(0.0, 0.99), (0.01, 0.98), (0.96, 0.97), (0.97, 0.96), (0.98, 0.01), (0.99, 0.0)]

        self.assertListEqual([(o[0], r) for o, r in ReverseRanking(self.rawRankedData)], expected)

    def test_ReverseRankingNormal(self):
        expected = [(0.99, 5), (0.98, 4), (0.97, 3), (0.96, 2), (0.01, 1), (0, 0)]

        self.assertListEqual([(o[0], r) for o, r in ReverseRanking(self.normalRankedData)], expected)


if __name__ == '__main__':
    unittest.main()
