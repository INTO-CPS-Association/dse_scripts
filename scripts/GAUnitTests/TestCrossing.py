import unittest
from genetic import Crossings

class TestCrossing(unittest.TestCase):
    def test_CheckParentsNoError(self):
        tests = [({0: 2}, {0: 1}),
                 ({0: 2, "a": "yes"}, {0: 1, "a": "no"})]

        for p1, p2 in tests:
            with self.subTest(msg=f"P1: {p1} | P2: {p2}"):
                Crossings.CheckParents(p1, p2)

    def test_CheckParentsError(self):
        tests = [({1: 2}, {0: 1}, ValueError),
                 ({0: 2, "a": 1}, {0: 1, "a": "no"}, ValueError),
                 ({0: 2, "a": "1", 1: 0}, {0: 1, "a": "no"}, ValueError)]

        for p1, p2, expected in tests:
            with self.subTest(msg=f"P1: {p1} | P2: {p2}"):
                with self.assertRaises(expected):
                    Crossings.CheckParents(p1, p2)

    def test_NPointCrossing(self):
        tests = [({0: 2}, {0: 1}, 1, [{0: 1}]),
                 ({0: 2}, {0: 1}, 0, [{0: 2}]),
                 ({0: 2, 1: 2}, {0: 1, 1: 1}, 0, [{0: 2, 1: 2}]),
                 ({0: 2, 1: 2}, {0: 1, 1: 1}, 1, [{0: 1, 1: 1}, {0: 2, 1: 1}]),
                 ({0: 2, 1: 2, 3: 2}, {0: 1, 1: 1, 3: 2}, 2, [{0: 1, 1: 1, 3: 2}, {0: 2, 1: 1, 3: 2}, {0: 1, 1: 2, 3: 2}])]

        for p1, p2, nPoints, expected in tests:
            with self.subTest(msg=f"P1: {p1}| P2: {p2}| Points: {nPoints}| Expected: {expected}"):
                self.assertIn(Crossings.NPointCrossing(p1, p2, nPoints), expected)

    def test_UniformCrossing(self):
        tests = [({0: 2}, {0: 1}, [{0: 1}, {0: 2}]),
                 ({0: 2, 1: 2}, {0: 1, 1: 1}, [{0: 2, 1: 2}, {0: 1, 1: 1}, {0: 2, 1: 1}, {0: 1, 1: 2}])]

        for i in range(100):
            for p1, p2, expected in tests:
                with self.subTest(msg=f"P1: {p1} | P2: {p2} | Expected: {expected}"):
                    self.assertIn(Crossings.UniformCrossing(p1, p2), expected)

    def test_BLX(self):
        tests = [({0: 0.3}, {0: 0.4}, "0.25 <= r[0] <= 0.45"),
                 ({0: 0.5}, {0: 0.6}, "0.45 <= r[0] <= 0.65"),
                 ({0: 0.5, 1: 0.3}, {0: 0.6, 1: 0.4}, "0.45 <= r[0] <= 0.65 and 0.25 <= r[1] <= 0.45")]

        for i in range(100):
            for p1, p2, ev in tests:
                with self.subTest(msg=f"P1: {p1} | P2: {p2} | Test: {ev}"):
                    r = Crossings.BLX(p1, p2, [])
                    self.assertTrue(type(r) is type(p1) and type(r) is type(p2))
                    self.assertTrue(eval(ev))


if __name__ == '__main__':
    unittest.main()
