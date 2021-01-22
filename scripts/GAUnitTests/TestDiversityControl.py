import unittest

from genetic.DiversityControl import EulerDistance


class TestDiversityControl(unittest.TestCase):
    def setUp(self):
        self.testData = [({0: 0}, 0, 0), ({0: 0.01}, 0.01, 0.01), ({0: 0.99}, 0.99, 0.99), ({0: 0.98}, 0.98, 0.98), ({0: 0.97}, 0.97, 0.97), ({0: 0.96}, 0.96, 0.96)]

    def test_EulerDiversityMaximise(self):
        result = EulerDistance(self.testData, True, 0.1, 0.1)

        self.assertListEqual([round(k, 3) for _, k, _ in result], [0.0, 0.005, 0.247, 0.245, 0.242, 0.24])

    def test_EulerDiversityMinimise(self):
        result = EulerDistance(self.testData, False, 0.1, 0.1)

        self.assertListEqual([round(k, 3) for _, k, _ in result], [3.96, 3.98, 7.92, 7.88, 7.84, 7.8])


if __name__ == '__main__':
    unittest.main()
