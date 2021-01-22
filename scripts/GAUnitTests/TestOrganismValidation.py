import unittest
from genetic import OrganismValidation

class TestOrganismValidation(unittest.TestCase):

    def test_ReplaceWithQualifiedNames(self):
        tests = [({"a": 0}, "a == 0", "organism['a'] == 0"),
                 ({"a": 0}, "a == a", "organism['a'] == organism['a']"),
                 ({"a": 0, "b": 1}, "a == a", "organism['a'] == organism['a']"),
                 ({"a": 0, "b": 1}, "a == a + 1", "organism['a'] == organism['a'] + 1"),
                 ({"a": 0, "b": 1}, "a == b", "organism['a'] == organism['b']"),
                 ({"a": 0, "b": 1}, "b == a", "organism['b'] == organism['a']"),
                 ({"a": 0, "b": 1}, "c == c", "c == c"),
                 ({"a": 0, "b": 1, "ac": 2}, "ac == 2", "organism['ac'] == 2"),
                 ({"a": 0, "b": 1}, "ac == c", "ac == c"),
                 ({"{test}.fmuTest.Something": 7}, "{test}.fmuTest.Something {test}.fmuTest.Somethingelse", "organism['{test}.fmuTest.Something'] {test}.fmuTest.Somethingelse"),
                 ({"{test}.fmuTest.Something": 7}, "{test}.fmuTest.Something {test}NfmuTest.Something", "organism['{test}.fmuTest.Something'] {test}NfmuTest.Something"),
                 ({"{test}.fmuTest.Something": 7}, "{test}.fmuTest.Something={test}.fmuTest.Somethingelse", "organism['{test}.fmuTest.Something']={test}.fmuTest.Somethingelse"),
                 ({"{test}.fmuTest.Something2": 7, "{test}.fmuTest.Something21": 0}, "{test}.fmuTest.Something2={test}.fmuTest.Somethingelse21", "organism['{test}.fmuTest.Something2']={test}.fmuTest.Somethingelse21")]

        for org, constraint, expected in tests:
            with self.subTest(msg=f"Expected: {expected} with org {org} and constraint {constraint}"):
                self.assertEqual(OrganismValidation.ReplaceWithQualifiedNames(org, constraint), expected)

    def test_CheckOrganismConstraints(self):
        tests = [({"a": 0}, ["a == 0"], True),
                 ({"a": 0}, ["a == a"], True),
                 ({"a": 0}, ["a == 1"], False),
                 ({"a": 0, "b": 1}, ["a == a"], True),
                 ({"a": 0, "b": 1}, ["a == b"], False),
                 ({"a": 0, "b": 1}, ["b == a"], False),
                 ({"a": 0, "b": 1}, ["b == a", "a == a"], False),
                 ({"a": 0, "b": 1}, ["b == a + 1", "a == a"], True),
                 ({"a": 0, "b": 1, "ac": 2}, ["ac == 2"], True),
                 ({"a": 0, "b": 1, "ac": 2}, ["ac == a"], False),]

        for organism, constraint, expected in tests:
            with self.subTest(msg=f"Expected: {expected} with org {organism} and constraint {constraint}"):
                self.assertEquals(OrganismValidation.CheckOrganismConstraints(organism, constraint), expected)

    def test_BoundOrganisms(self):
        tests = [([{"a": 0}], {"a": [0, 1]}, [{"a": 0}]),
                 ([{"a": 0}], {"a": [-2, -1]}, [{"a": -1}]),
                 ([{"a": -100}], {"a": [-2, -1]}, [{"a": -2}]),
                 ([{"a": 0, "b": 100}], {"a": [0, 1]}, [{"a": 0, "b": 100}]),
                 ([{"a": 0, "b": 100}], {"a": [1, 10]}, [{"a": 1, "b": 100}]),
                 ([{"a": 0, "b": 100}], {"a": [1, 10], "b": [-10, -1]}, [{"a": 1, "b": -1}]),
                 ([{"a": 0, "b": -100}], {"a": [1, 10], "b": [-10, -1]}, [{"a": 1, "b": -10}]),
                 ([{"a": 0, "b": -100, "ac": 5}], {"a": [1, 10], "b": [-10, -1]}, [{"a": 1, "b": -10, "ac": 5}])]

        for organism, constraint, expected in tests:
            with self.subTest(msg=f"Expected: {expected} with org {organism} and constraint {constraint}"):
                self.assertListEqual(OrganismValidation.BoundOrganisms(organism, constraint), expected)


if __name__ == '__main__':
    unittest.main()
