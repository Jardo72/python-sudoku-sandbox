#
# Copyright 2018 Jaroslav Chmurny
#
# This file is part of Python Sudoku Sandbox.
#
# Python Sudoku Sandbox is free software developed for educational and
# experimental purposes. It is licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
This module is a collection of integration tests covering more or less the entire functionality
end-to-end. In practical terms, the test cases provided by this test fixture involve parsing of
the puzzle, invocation of the search engine (which in turn invokes the search algorithms), and
formatting of the grid representing the found solution. When designing these test cases, I kept
the following testing objectives in mind:
* Complete coverage of all search algorithms.
* Scenarios with valid puzzles that do not violate the rules as well as scenarios with invalid
  puzzles that contain a duplicate in a row, column, or region and should be thus immediately
  rejected by the search engine.
* Complete coverage of all possible search outcomes (solution found, both kinds of dead end,
  plus timeout).
"""

from logging import basicConfig, INFO
from unittest import TestCase

from gridio import PuzzleParser, GridFormatter
from algorithmregistry import NoSuchAlgorithmError
from searchengine import SearchEngine, SearchOutcome, InvalidPuzzleError


class TestSearchEngine:
    """
    Simple helper class that combines the parsing of a puzzle, the invocation of the search
    engine, plus the formatting of the final grid to a single method.
    """

    @staticmethod
    def find_solution(puzzle, algorithm, timeout_sec = 10):
        cell_values = PuzzleParser.read_from_string(puzzle)
        search_summary = SearchEngine.find_solution(cell_values, algorithm, timeout_sec)
        formatted_final_grid = GridFormatter.write_to_string(search_summary.final_grid)
        return (search_summary, formatted_final_grid)


class AbstractSolutionFoundTests(TestCase):
    """
    Base class providing functionality common to test fixtures covering the case when
    a puzzle is successfully solved by a search algorithm.
    """

    def verify_that_proper_solution_is_found(self, puzzle, expected_solution):
        for algorithm in self.algorithms:
            with self.subTest(algorithm = algorithm):
                search_summary, actual_solution = TestSearchEngine.find_solution(puzzle, algorithm, timeout_sec = 60)
                self.assertEqual(SearchOutcome.SOLUTION_FOUND, search_summary.outcome)
                self.__assertEquivalent(expected_solution, actual_solution)


    def __assertEquivalent(self, expected_output, actual_output):
        expected_output = expected_output.strip()
        actual_output = actual_output.strip()
        self.assertEqual(expected_output, actual_output)


class UnambiguousPuzzleSolutionFoundTests(AbstractSolutionFoundTests):
    """
    Collection of integration tests covering the case when an unambiguous puzzle is successfully
    solved by various search algorithms.
    """

    @property
    def algorithms(self):
        return ["UCS", "Smart-DFS", "Smart-BFS"]


    def test_case_01(self):
        puzzle = """
+-------+-------+-------+
| 6     |     4 |   8 5 |
| 9 7   |   6 5 |       |
|   4 8 | 7 3   |       |
+-------+-------+-------+
|   8   | 2 4 7 |       |
|     6 |   8   | 5     |
|       | 1 5 6 |   4   |
+-------+-------+-------+
|       |   1 3 | 2 6   |
|       | 6 9   |   3 4 |
| 2 6   | 4     |     9 |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 6 3 1 | 9 2 4 | 7 8 5 |
| 9 7 2 | 8 6 5 | 4 1 3 |
| 5 4 8 | 7 3 1 | 9 2 6 |
+-------+-------+-------+
| 3 8 5 | 2 4 7 | 6 9 1 |
| 4 1 6 | 3 8 9 | 5 7 2 |
| 7 2 9 | 1 5 6 | 3 4 8 |
+-------+-------+-------+
| 8 9 4 | 5 1 3 | 2 6 7 |
| 1 5 7 | 6 9 2 | 8 3 4 |
| 2 6 3 | 4 7 8 | 1 5 9 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_02(self):
        puzzle = """
+-------+-------+-------+
| 9   2 |       | 5 4 3 |
|     1 |       | 2     |
|       | 6 2   | 1 8   |
+-------+-------+-------+
|   1 5 |     3 |   2   |
|   8   | 4   1 |   7   |
|   9   | 2     | 4 6   |
+-------+-------+-------+
|   3 9 |   4 6 |       |
|     7 |       | 8     |
| 1 4 8 |       | 6   9 |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 9 6 2 | 1 8 7 | 5 4 3 |
| 8 7 1 | 5 3 4 | 2 9 6 |
| 3 5 4 | 6 2 9 | 1 8 7 |
+-------+-------+-------+
| 4 1 5 | 7 6 3 | 9 2 8 |
| 2 8 6 | 4 9 1 | 3 7 5 |
| 7 9 3 | 2 5 8 | 4 6 1 |
+-------+-------+-------+
| 5 3 9 | 8 4 6 | 7 1 2 |
| 6 2 7 | 9 1 5 | 8 3 4 |
| 1 4 8 | 3 7 2 | 6 5 9 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_03(self):
        puzzle = """
+-------+-------+-------+
| 7     | 1   9 |       |
|   3   | 4   6 |   2   |
| 6 5   |   3   | 9     |
+-------+-------+-------+
|     9 | 7 6   | 1   2 |
| 2   7 |       | 3   9 |
| 5   3 |   9 1 | 4     |
+-------+-------+-------+
|     6 |   1   |   9 4 |
|   9   | 6   5 |   7   |
|       | 9   4 |     6 |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 7 4 8 | 1 2 9 | 6 3 5 |
| 9 3 1 | 4 5 6 | 7 2 8 |
| 6 5 2 | 8 3 7 | 9 4 1 |
+-------+-------+-------+
| 4 8 9 | 7 6 3 | 1 5 2 |
| 2 1 7 | 5 4 8 | 3 6 9 |
| 5 6 3 | 2 9 1 | 4 8 7 |
+-------+-------+-------+
| 8 7 6 | 3 1 2 | 5 9 4 |
| 1 9 4 | 6 8 5 | 2 7 3 |
| 3 2 5 | 9 7 4 | 8 1 6 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_04(self):
        puzzle = """
+-------+-------+-------+
|   1   |   8   |   7   |
|       |     9 | 5   3 |
| 9     | 7   5 |   4 1 |
+-------+-------+-------+
| 8 5   |   9   |   6 4 |
|     7 |       | 3     |
| 6 3   |   7   |   5 2 |
+-------+-------+-------+
| 7 9   | 3   1 |     6 |
| 5   1 | 2     |       |
|   2   |   6   |   1   |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 3 1 5 | 4 8 2 | 6 7 9 |
| 2 7 4 | 6 1 9 | 5 8 3 |
| 9 8 6 | 7 3 5 | 2 4 1 |
+-------+-------+-------+
| 8 5 2 | 1 9 3 | 7 6 4 |
| 1 4 7 | 5 2 6 | 3 9 8 |
| 6 3 9 | 8 7 4 | 1 5 2 |
+-------+-------+-------+
| 7 9 8 | 3 5 1 | 4 2 6 |
| 5 6 1 | 2 4 8 | 9 3 7 |
| 4 2 3 | 9 6 7 | 8 1 5 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_05(self):
        puzzle = """
+-------+-------+-------+
| 2 9 1 |       |       |
|   5   | 9   2 |       |
|   4 6 | 3   7 |   9 5 |
+-------+-------+-------+
| 6     | 1 3 4 |       |
|       |       |       |
|       | 2 8 5 |     9 |
+-------+-------+-------+
| 9 8   | 5   1 | 6 4   |
|       | 7   8 |   5   |
|       |       | 1 2 8 |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 2 9 1 | 8 5 6 | 3 7 4 |
| 3 5 7 | 9 4 2 | 8 1 6 |
| 8 4 6 | 3 1 7 | 2 9 5 |
+-------+-------+-------+
| 6 7 9 | 1 3 4 | 5 8 2 |
| 5 2 8 | 6 7 9 | 4 3 1 |
| 1 3 4 | 2 8 5 | 7 6 9 |
+-------+-------+-------+
| 9 8 3 | 5 2 1 | 6 4 7 |
| 4 1 2 | 7 6 8 | 9 5 3 |
| 7 6 5 | 4 9 3 | 1 2 8 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_06(self):
        puzzle = """
+-------+-------+-------+
|     1 |   7   | 9     |
|       |     9 |   1 5 |
| 7     | 1   4 | 3   8 |
+-------+-------+-------+
| 9   5 |   8   | 4   7 |
|   4   |       |   8   |
| 6   7 |   3   | 5   2 |
+-------+-------+-------+
| 1   6 | 5   8 |     3 |
| 4 5   | 3     |       |
|     8 |   2   | 1     |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 5 2 1 | 8 7 3 | 9 4 6 |
| 8 3 4 | 2 6 9 | 7 1 5 |
| 7 6 9 | 1 5 4 | 3 2 8 |
+-------+-------+-------+
| 9 1 5 | 6 8 2 | 4 3 7 |
| 2 4 3 | 7 9 5 | 6 8 1 |
| 6 8 7 | 4 3 1 | 5 9 2 |
+-------+-------+-------+
| 1 9 6 | 5 4 8 | 2 7 3 |
| 4 5 2 | 3 1 7 | 8 6 9 |
| 3 7 8 | 9 2 6 | 1 5 4 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_07(self):
        puzzle = """
+-------+-------+-------+
|       |     8 | 1   6 |
| 5     | 1   9 |   7 4 |
|   1   |   5   |   8   |
+-------+-------+-------+
| 8 6   |   4   |   9 5 |
|     9 |       | 4     |
| 2 5   |   7   |   6 3 |
+-------+-------+-------+
|   4   |   3   |   1   |
| 1 2   | 6   4 |     7 |
| 9   6 | 7     |       |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 4 9 7 | 3 2 8 | 1 5 6 |
| 5 8 2 | 1 6 9 | 3 7 4 |
| 6 1 3 | 4 5 7 | 9 8 2 |
+-------+-------+-------+
| 8 6 1 | 2 4 3 | 7 9 5 |
| 3 7 9 | 5 8 6 | 4 2 1 |
| 2 5 4 | 9 7 1 | 8 6 3 |
+-------+-------+-------+
| 7 4 5 | 8 3 2 | 6 1 9 |
| 1 2 8 | 6 9 4 | 5 3 7 |
| 9 3 6 | 7 1 5 | 2 4 8 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


class AmbiguousPuzzleSolutionFoundTests(AbstractSolutionFoundTests):
    """
    Collection of integration tests covering the case when an ambiguous puzzle is successfully
    solved by various brute search algorithms.
    """

    @property
    def algorithms(self):
        return ["Smart-DFS", "Smart-BFS"]


    def test_case_01(self):
        puzzle = """
+-------+-------+-------+
|   8   | 1     |   6   |
|     1 | 2   8 | 3     |
|     4 | 6     |   8   |
+-------+-------+-------+
| 7 5   |       |       |
|       | 5   3 |       |
|       |       |   2 3 |
+-------+-------+-------+
|   2   |     1 | 8     |
|     6 | 8   5 | 1     |
|   3   |     2 |   4   |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 2 8 5 | 1 3 4 | 9 6 7 |
| 6 7 1 | 2 9 8 | 3 5 4 |
| 3 9 4 | 6 5 7 | 2 8 1 |
+-------+-------+-------+
| 7 5 3 | 4 2 9 | 6 1 8 |
| 8 6 2 | 5 1 3 | 4 7 9 |
| 4 1 9 | 7 8 6 | 5 2 3 |
+-------+-------+-------+
| 5 2 7 | 3 4 1 | 8 9 6 |
| 9 4 6 | 8 7 5 | 1 3 2 |
| 1 3 8 | 9 6 2 | 7 4 5 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_02(self):
        puzzle = """
+-------+-------+-------+
|   9   |   5   |       |
|       |       | 9 3 7 |
|       |   6 8 |   5   |
+-------+-------+-------+
| 5     |       | 1     |
|   6   | 1   7 |   9   |
|     2 |       |     8 |
+-------+-------+-------+
|   5   | 3 2   |       |
| 1 3 8 |       |       |
|       |   9   |   4   |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 2 9 4 | 7 5 3 | 8 1 6 |
| 6 8 5 | 4 1 2 | 9 3 7 |
| 3 7 1 | 9 6 8 | 2 5 4 |
+-------+-------+-------+
| 5 4 7 | 2 8 9 | 1 6 3 |
| 8 6 3 | 1 4 7 | 5 9 2 |
| 9 1 2 | 6 3 5 | 4 7 8 |
+-------+-------+-------+
| 4 5 9 | 3 2 6 | 7 8 1 |
| 1 3 8 | 5 7 4 | 6 2 9 |
| 7 2 6 | 8 9 1 | 3 4 5 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_03(self):
        puzzle = """
+-------+-------+-------+
|       |   9 2 |   3   |
|   3 7 |       |   9   |
|   4   | 7     |       |
+-------+-------+-------+
| 2     |     5 | 6     |
| 8     |   6   |     7 |
|     5 | 4     |     3 |
+-------+-------+-------+
|       |     7 |   6   |
|   5   |       | 1 7   |
|   2   | 9 8   |       |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 5 6 8 | 1 9 2 | 7 3 4 |
| 1 3 7 | 8 4 6 | 5 9 2 |
| 9 4 2 | 7 5 3 | 8 1 6 |
+-------+-------+-------+
| 2 9 4 | 3 7 5 | 6 8 1 |
| 8 1 3 | 2 6 9 | 4 5 7 |
| 6 7 5 | 4 1 8 | 9 2 3 |
+-------+-------+-------+
| 4 8 1 | 5 3 7 | 2 6 9 |
| 3 5 9 | 6 2 4 | 1 7 8 |
| 7 2 6 | 9 8 1 | 3 4 5 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_04(self):
        puzzle = """
+-------+-------+-------+
|   5   | 6 9   |   4   |
|   8 2 |       | 6     |
|       |       |     5 |
+-------+-------+-------+
|     3 |   5   |     7 |
|     8 |       | 3     |
| 6     |   7   | 4     |
+-------+-------+-------+
| 7     |       |       |
|     6 |       | 5 1   |
|   9   |   1 2 |   7   |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 3 5 7 | 6 9 1 | 2 4 8 |
| 4 8 2 | 7 3 5 | 6 9 1 |
| 1 6 9 | 4 2 8 | 7 3 5 |
+-------+-------+-------+
| 2 4 3 | 8 5 9 | 1 6 7 |
| 9 7 8 | 1 6 4 | 3 5 2 |
| 6 1 5 | 2 7 3 | 4 8 9 |
+-------+-------+-------+
| 7 3 1 | 5 8 6 | 9 2 4 |
| 8 2 6 | 9 4 7 | 5 1 3 |
| 5 9 4 | 3 1 2 | 8 7 6 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_05(self):
        puzzle = """
+-------+-------+-------+
|       |     7 |     8 |
|       | 3     |     6 |
|     9 |   1   |   3 5 |
+-------+-------+-------+
|       |   6   |   5   |
|   1 3 |       | 9 7   |
|   8   |   4   |       |
+-------+-------+-------+
| 5 3   |   9   | 2     |
| 4     |     8 |       |
| 9     | 6     |       |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 3 6 2 | 4 5 7 | 1 9 8 |
| 1 5 7 | 3 8 9 | 4 2 6 |
| 8 4 9 | 2 1 6 | 7 3 5 |
+-------+-------+-------+
| 2 9 4 | 7 6 1 | 8 5 3 |
| 6 1 3 | 8 2 5 | 9 7 4 |
| 7 8 5 | 9 4 3 | 6 1 2 |
+-------+-------+-------+
| 5 3 6 | 1 9 4 | 2 8 7 |
| 4 2 1 | 5 7 8 | 3 6 9 |
| 9 7 8 | 6 3 2 | 5 4 1 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_06(self):
        puzzle = """
+-------+-------+-------+
|     1 |   5   |       |
|       |   8 7 | 5     |
|       |       | 2 1 4 |
+-------+-------+-------+
| 5     |       |   6   |
|     8 | 6   4 | 1     |
|   3   |       |     7 |
+-------+-------+-------+
| 6 7 2 |       |       |
|     5 | 2 3   |       |
|       |   1   | 9     |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 3 9 1 | 4 5 2 | 6 7 8 |
| 2 6 4 | 1 8 7 | 5 3 9 |
| 8 5 7 | 9 6 3 | 2 1 4 |
+-------+-------+-------+
| 5 4 9 | 3 7 1 | 8 6 2 |
| 7 2 8 | 6 9 4 | 1 5 3 |
| 1 3 6 | 8 2 5 | 4 9 7 |
+-------+-------+-------+
| 6 7 2 | 5 4 9 | 3 8 1 |
| 9 1 5 | 2 3 8 | 7 4 6 |
| 4 8 3 | 7 1 6 | 9 2 5 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_07(self):
        puzzle = """
+-------+-------+-------+
|       |   4 5 |   6   |
|       |       | 1 3 9 |
|   1   |   6   |       |
+-------+-------+-------+
| 6     |       | 2     |
|   4   | 2   9 |   1   |
|     7 |       |     5 |
+-------+-------+-------+
|       |   1   |   8   |
| 2 3 5 |       |       |
|   6   | 3 7   |       |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 3 9 2 | 1 4 5 | 7 6 8 |
| 4 5 6 | 8 2 7 | 1 3 9 |
| 7 1 8 | 9 6 3 | 5 2 4 |
+-------+-------+-------+
| 6 8 9 | 7 5 1 | 2 4 3 |
| 5 4 3 | 2 8 9 | 6 1 7 |
| 1 2 7 | 4 3 6 | 8 9 5 |
+-------+-------+-------+
| 9 7 4 | 5 1 2 | 3 8 6 |
| 2 3 5 | 6 9 8 | 4 7 1 |
| 8 6 1 | 3 7 4 | 9 5 2 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_08(self):
        puzzle = """
+-------+-------+-------+
| 5     |   3 6 |       |
|     4 |       |   2 8 |
|       |     4 | 9     |
+-------+-------+-------+
| 9 3   |     1 |       |
|       | 6     | 5   7 |
|     1 |   2   |       |
+-------+-------+-------+
|   6   |   1   |   8   |
| 8     | 3     | 4 9   |
|   5   |       |       |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 5 8 2 | 9 3 6 | 1 7 4 |
| 3 9 4 | 1 5 7 | 6 2 8 |
| 7 1 6 | 2 8 4 | 9 5 3 |
+-------+-------+-------+
| 9 3 5 | 4 7 1 | 8 6 2 |
| 2 4 8 | 6 9 3 | 5 1 7 |
| 6 7 1 | 5 2 8 | 3 4 9 |
+-------+-------+-------+
| 4 6 3 | 7 1 9 | 2 8 5 |
| 8 2 7 | 3 6 5 | 4 9 1 |
| 1 5 9 | 8 4 2 | 7 3 6 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_09(self):
        puzzle = """
+-------+-------+-------+
|     5 |   9   | 8     |
|   3   |       |   2   |
| 8     | 4   1 |     7 |
+-------+-------+-------+
|     2 |       | 7     |
| 3     |   8   |     5 |
|     6 |       | 9     |
+-------+-------+-------+
| 9     | 6   5 |     1 |
|   7   |       |   6   |
|     3 |   4   | 5     |
+-------+-------+-------+"""
        expected_solution = """
+-------+-------+-------+
| 7 1 5 | 3 9 2 | 8 4 6 |
| 6 3 4 | 5 7 8 | 1 2 9 |
| 8 2 9 | 4 6 1 | 3 5 7 |
+-------+-------+-------+
| 1 8 2 | 9 5 6 | 7 3 4 |
| 3 9 7 | 2 8 4 | 6 1 5 |
| 4 5 6 | 7 1 3 | 9 8 2 |
+-------+-------+-------+
| 9 4 8 | 6 3 5 | 2 7 1 |
| 5 7 1 | 8 2 9 | 4 6 3 |
| 2 6 3 | 1 4 7 | 5 9 8 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_10(self):
        puzzle = """
+-------+-------+-------+
|       | 8     |       |
|     1 |   9   | 4     |
|   5   |     4 |   9   |
+-------+-------+-------+
|     5 |   4   |     7 |
|   2   | 9   6 |   4   |
| 9     |   5   | 8     |
+-------+-------+-------+
|   3   | 2     |   6   |
|     7 |   8   | 5     |
|       |     3 |       |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 4 9 2 | 8 3 7 | 6 5 1 |
| 3 7 1 | 6 9 5 | 4 8 2 |
| 8 5 6 | 1 2 4 | 7 9 3 |
+-------+-------+-------+
| 6 1 5 | 3 4 8 | 9 2 7 |
| 7 2 8 | 9 1 6 | 3 4 5 |
| 9 4 3 | 7 5 2 | 8 1 6 |
+-------+-------+-------+
| 5 3 4 | 2 7 9 | 1 6 8 |
| 2 6 7 | 4 8 1 | 5 3 9 |
| 1 8 9 | 5 6 3 | 2 7 4 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_11(self):
        puzzle = """
+-------+-------+-------+
|     9 |     8 |     4 |
|   5   |   6   |   8   |
| 7     | 1     | 9     |
+-------+-------+-------+
| 3     | 6     | 2     |
|   2   |   1   |   9   |
|     7 |     5 |     6 |
+-------+-------+-------+
|     6 |     3 |     1 |
|   4   |   7   |   3   |
| 2     | 8     | 4     |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 1 6 9 | 5 3 8 | 7 2 4 |
| 4 5 2 | 7 6 9 | 1 8 3 |
| 7 8 3 | 1 4 2 | 9 6 5 |
+-------+-------+-------+
| 3 9 5 | 6 8 4 | 2 1 7 |
| 6 2 4 | 3 1 7 | 5 9 8 |
| 8 1 7 | 2 9 5 | 3 4 6 |
+-------+-------+-------+
| 9 7 6 | 4 2 3 | 8 5 1 |
| 5 4 8 | 9 7 1 | 6 3 2 |
| 2 3 1 | 8 5 6 | 4 7 9 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_12(self):
        puzzle = """
+-------+-------+-------+
|       |   4   |       |
|   5   |       |     8 |
| 4   8 | 3   6 |   7   |
+-------+-------+-------+
|     3 |     1 |   5 4 |
|     1 | 7   9 | 6     |
| 9 6   | 4     | 8     |
+-------+-------+-------+
|   8   | 6   3 | 7   2 |
| 3     |       |   4   |
|       |   9   |       |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 7 3 9 | 5 4 8 | 2 6 1 |
| 2 5 6 | 9 1 7 | 4 3 8 |
| 4 1 8 | 3 2 6 | 5 7 9 |
+-------+-------+-------+
| 8 7 3 | 2 6 1 | 9 5 4 |
| 5 4 1 | 7 8 9 | 6 2 3 |
| 9 6 2 | 4 3 5 | 8 1 7 |
+-------+-------+-------+
| 1 8 4 | 6 5 3 | 7 9 2 |
| 3 9 5 | 8 7 2 | 1 4 6 |
| 6 2 7 | 1 9 4 | 3 8 5 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_13(self):
        puzzle = """
+-------+-------+-------+
|   5   |       |       |
|   8   |     6 | 3   4 |
|     9 |       |     7 |
+-------+-------+-------+
|       |       |   4   |
| 2     | 3     |   5   |
|   6 3 |       | 7 9   |
+-------+-------+-------+
|       | 8 2   | 6 7 9 |
|       | 6   7 |   3   |
|     2 |       | 8     |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 4 5 6 | 7 3 2 | 9 8 1 |
| 7 8 1 | 9 5 6 | 3 2 4 |
| 3 2 9 | 1 8 4 | 5 6 7 |
+-------+-------+-------+
| 9 1 7 | 5 6 8 | 2 4 3 |
| 2 4 8 | 3 7 9 | 1 5 6 |
| 5 6 3 | 2 4 1 | 7 9 8 |
+-------+-------+-------+
| 1 3 4 | 8 2 5 | 6 7 9 |
| 8 9 5 | 6 1 7 | 4 3 2 |
| 6 7 2 | 4 9 3 | 8 1 5 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_14(self):
        puzzle = """
+-------+-------+-------+
|   2   | 5   6 |   8   |
| 5 6   |       | 4   9 |
|   1   |   2   | 6 5   |
+-------+-------+-------+
|       |     1 |       |
| 2   3 |     8 |       |
|       |       | 9     |
+-------+-------+-------+
| 9     | 3   2 |   6   |
|       | 9     | 3   1 |
| 6     | 8 1   |       |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 4 2 9 | 5 7 6 | 1 8 3 |
| 5 6 7 | 1 8 3 | 4 2 9 |
| 3 1 8 | 4 2 9 | 6 5 7 |
+-------+-------+-------+
| 7 9 6 | 2 5 1 | 8 3 4 |
| 2 4 3 | 7 9 8 | 5 1 6 |
| 1 8 5 | 6 3 4 | 9 7 2 |
+-------+-------+-------+
| 9 5 1 | 3 4 2 | 7 6 8 |
| 8 7 2 | 9 6 5 | 3 4 1 |
| 6 3 4 | 8 1 7 | 2 9 5 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_15(self):
        puzzle = """
+-------+-------+-------+
|       |   3   |       |
| 9     | 7     | 6     |
| 7     |   1   |   8 3 |
+-------+-------+-------+
|       |   4 1 | 7   6 |
| 4   9 |   7   |     5 |
|       |     3 |       |
+-------+-------+-------+
|   6   |       | 1 9   |
|     3 |     7 |       |
| 8     |       | 4   7 |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 2 1 8 | 5 3 6 | 9 7 4 |
| 9 3 4 | 7 8 2 | 6 5 1 |
| 7 5 6 | 4 1 9 | 2 8 3 |
+-------+-------+-------+
| 3 8 5 | 9 4 1 | 7 2 6 |
| 4 2 9 | 6 7 8 | 3 1 5 |
| 6 7 1 | 2 5 3 | 8 4 9 |
+-------+-------+-------+
| 5 6 7 | 3 2 4 | 1 9 8 |
| 1 4 3 | 8 9 7 | 5 6 2 |
| 8 9 2 | 1 6 5 | 4 3 7 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


class SimplePuzzleSolutionFoundEvenByNaiveAlgorithmTests(AbstractSolutionFoundTests):
    """
    Collection of integration tests covering the case when a very simple puzzle is successfully
    solved by various search algorithms including naive ones.
    """

    @property
    def algorithms(self):
        return ["UCS", "Smart-DFS", "Smart-BFS", "Naive-DFS", "Naive-BFS"]


    def test_case_01(self):
        puzzle = """
+-------+-------+-------+
|   8 5 | 1 3 4 | 9 6 7 |
| 6 7 1 | 2   8 | 3 5 4 |
| 3 9 4 | 6 5 7 | 2 8   |
+-------+-------+-------+
| 7   3 | 4 2 9 | 6 1   |
| 8 6 2 | 5 1   |   7 9 |
| 4 1   | 7 8 6 | 5 2 3 |
+-------+-------+-------+
| 5 2 7 | 3 4 1 | 8 9 6 |
| 9 4 6 |   7 5 | 1 3 2 |
|   3 8 | 9 6 2 | 7   5 |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 2 8 5 | 1 3 4 | 9 6 7 |
| 6 7 1 | 2 9 8 | 3 5 4 |
| 3 9 4 | 6 5 7 | 2 8 1 |
+-------+-------+-------+
| 7 5 3 | 4 2 9 | 6 1 8 |
| 8 6 2 | 5 1 3 | 4 7 9 |
| 4 1 9 | 7 8 6 | 5 2 3 |
+-------+-------+-------+
| 5 2 7 | 3 4 1 | 8 9 6 |
| 9 4 6 | 8 7 5 | 1 3 2 |
| 1 3 8 | 9 6 2 | 7 4 5 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_02(self):
        puzzle = """
+-------+-------+-------+
| 2 9   |   5 3 | 8 1 6 |
| 6 8 5 | 4 1 2 |   3 7 |
|   7 1 | 9   8 | 2 5 4 |
+-------+-------+-------+
| 5 4 7 | 2   9 | 1 6 3 |
| 8 6 3 | 1 4 7 | 5 9   |
|   1 2 | 6 3 5 |   7 8 |
+-------+-------+-------+
| 4 5 9 | 3 2 6 | 7 8 1 |
| 1 3   |   7 4 | 6 2 9 |
| 7   6 | 8 9 1 |     5 |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 2 9 4 | 7 5 3 | 8 1 6 |
| 6 8 5 | 4 1 2 | 9 3 7 |
| 3 7 1 | 9 6 8 | 2 5 4 |
+-------+-------+-------+
| 5 4 7 | 2 8 9 | 1 6 3 |
| 8 6 3 | 1 4 7 | 5 9 2 |
| 9 1 2 | 6 3 5 | 4 7 8 |
+-------+-------+-------+
| 4 5 9 | 3 2 6 | 7 8 1 |
| 1 3 8 | 5 7 4 | 6 2 9 |
| 7 2 6 | 8 9 1 | 3 4 5 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_03(self):
        puzzle = """
+-------+-------+-------+
| 5 6 8 |   9 2 |   3 4 |
| 1 3 7 | 8 4 6 | 5 9 2 |
| 9   2 | 7 5   | 8 1   |
+-------+-------+-------+
| 2 9   | 3 7 5 | 6 8 1 |
| 8 1 3 | 2   9 | 4 5 7 |
| 6   5 | 4 1 8 | 9 2   |
+-------+-------+-------+
| 4   1 |   3 7 | 2 6 9 |
| 3 5 9 | 6 2 4 | 1 7 8 |
| 7 2 6 | 9 8   |     5 |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 5 6 8 | 1 9 2 | 7 3 4 |
| 1 3 7 | 8 4 6 | 5 9 2 |
| 9 4 2 | 7 5 3 | 8 1 6 |
+-------+-------+-------+
| 2 9 4 | 3 7 5 | 6 8 1 |
| 8 1 3 | 2 6 9 | 4 5 7 |
| 6 7 5 | 4 1 8 | 9 2 3 |
+-------+-------+-------+
| 4 8 1 | 5 3 7 | 2 6 9 |
| 3 5 9 | 6 2 4 | 1 7 8 |
| 7 2 6 | 9 8 1 | 3 4 5 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_04(self):
        puzzle = """
+-------+-------+-------+
| 3 5 7 | 6 9 1 |   4 8 |
|   8 2 |   3 5 | 6 9 1 |
| 1 6 9 | 4 2 8 | 7 3   |
+-------+-------+-------+
|   4 3 | 8 5 9 |   6 7 |
| 9 7 8 | 1   4 | 3   2 |
| 6 1 5 | 2 7   | 4 8 9 |
+-------+-------+-------+
| 7 3   | 5 8 6 |   2 4 |
|   2 6 | 9 4   | 5 1 3 |
| 5 9 4 | 3 1 2 | 8 7 6 |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 3 5 7 | 6 9 1 | 2 4 8 |
| 4 8 2 | 7 3 5 | 6 9 1 |
| 1 6 9 | 4 2 8 | 7 3 5 |
+-------+-------+-------+
| 2 4 3 | 8 5 9 | 1 6 7 |
| 9 7 8 | 1 6 4 | 3 5 2 |
| 6 1 5 | 2 7 3 | 4 8 9 |
+-------+-------+-------+
| 7 3 1 | 5 8 6 | 9 2 4 |
| 8 2 6 | 9 4 7 | 5 1 3 |
| 5 9 4 | 3 1 2 | 8 7 6 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_05(self):
        puzzle = """
+-------+-------+-------+
|   6 2 |   5 7 | 1 9   |
| 1 5   | 3 8   | 4 2 6 |
| 8 4 9 | 2 1 6 | 7 3   |
+-------+-------+-------+
| 2 9 4 | 7 6 1 | 8 5   |
|   1 3 |   2 5 | 9 7 4 |
| 7 8   | 9 4 3 | 6 1 2 |
+-------+-------+-------+
|   3 6 | 1 9 4 |   8 7 |
| 4 2 1 | 5   8 | 3 6 9 |
|   7 8 | 6   2 | 5 4   |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 3 6 2 | 4 5 7 | 1 9 8 |
| 1 5 7 | 3 8 9 | 4 2 6 |
| 8 4 9 | 2 1 6 | 7 3 5 |
+-------+-------+-------+
| 2 9 4 | 7 6 1 | 8 5 3 |
| 6 1 3 | 8 2 5 | 9 7 4 |
| 7 8 5 | 9 4 3 | 6 1 2 |
+-------+-------+-------+
| 5 3 6 | 1 9 4 | 2 8 7 |
| 4 2 1 | 5 7 8 | 3 6 9 |
| 9 7 8 | 6 3 2 | 5 4 1 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_06(self):
        puzzle = """
+-------+-------+-------+
| 3 9   |   5 2 | 6 7 8 |
| 2 6 4 | 1 8 7 | 5   9 |
| 8   7 |   6 3 | 2 1 4 |
+-------+-------+-------+
| 5 4 9 | 3   1 | 8 6 2 |
|   2 8 | 6 9 4 | 1 5 3 |
| 1 3 6 | 8 2 5 | 4 9   |
+-------+-------+-------+
|   7 2 | 5   9 | 3 8 1 |
| 9 1 5 |   3   | 7 4 6 |
| 4 8   | 7 1 6 |   2   |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 3 9 1 | 4 5 2 | 6 7 8 |
| 2 6 4 | 1 8 7 | 5 3 9 |
| 8 5 7 | 9 6 3 | 2 1 4 |
+-------+-------+-------+
| 5 4 9 | 3 7 1 | 8 6 2 |
| 7 2 8 | 6 9 4 | 1 5 3 |
| 1 3 6 | 8 2 5 | 4 9 7 |
+-------+-------+-------+
| 6 7 2 | 5 4 9 | 3 8 1 |
| 9 1 5 | 2 3 8 | 7 4 6 |
| 4 8 3 | 7 1 6 | 9 2 5 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


    def test_case_07(self):
        puzzle = """
+-------+-------+-------+
| 3 9 2 |   4 5 | 7 6 8 |
| 4 5 6 | 8 2 7 | 1   9 |
| 7 1   | 9 6 3 | 5 2   |
+-------+-------+-------+
| 6 8 9 | 7 5 1 | 2 4 3 |
|   4 3 |   8 9 |   1   |
| 1 2   |   3 6 | 8 9 5 |
+-------+-------+-------+
| 9 7   | 5 1   | 3   6 |
| 2 3 5 | 6 9 8 | 4 7 1 |
| 8 6   | 3 7 4 |   5 2 |
+-------+-------+-------+
"""
        expected_solution = """
+-------+-------+-------+
| 3 9 2 | 1 4 5 | 7 6 8 |
| 4 5 6 | 8 2 7 | 1 3 9 |
| 7 1 8 | 9 6 3 | 5 2 4 |
+-------+-------+-------+
| 6 8 9 | 7 5 1 | 2 4 3 |
| 5 4 3 | 2 8 9 | 6 1 7 |
| 1 2 7 | 4 3 6 | 8 9 5 |
+-------+-------+-------+
| 9 7 4 | 5 1 2 | 3 8 6 |
| 2 3 5 | 6 9 8 | 4 7 1 |
| 8 6 1 | 3 7 4 | 9 5 2 |
+-------+-------+-------+
"""
        self.verify_that_proper_solution_is_found(puzzle, expected_solution)


class AmbiguousPuzzlesLeadingToTimeoutTests(TestCase):
    """
    Collection of integration tests covering the case when a search fails because of timeout.
    """

    def test_case_01(self):
        puzzle = """
+-------+-------+-------+
|   7   |       |   1   |
| 5     |     6 |     7 |
|     1 |   8   | 5     |
+-------+-------+-------+
|   2   |       |   7   |
|       |   2   |       |
|   3   |       |   9   |
+-------+-------+-------+
|       |   9   | 8     |
| 9     | 6   4 |     3 |
|   5   |       |     4 |
+-------+-------+-------+
"""
        self.__test_that_search_leads_to_timeout(puzzle)


    def test_case_02(self):
        puzzle = """
+-------+-------+-------+
|       |   1 2 |       |
|       |       | 6 7   |
|     9 |       |       |
+-------+-------+-------+
|       |       | 5 9   |
|       |   8 7 |       |
| 6 9   |       |       |
+-------+-------+-------+
|       | 7   4 |       |
| 2     |       |     1 |
|   5   |       |   4   |
+-------+-------+-------+
"""
        self.__test_that_search_leads_to_timeout(puzzle)


    def test_case_03(self):
        puzzle = """
+-------+-------+-------+
| 7     |   2   |   5   |
|       | 3     | 4     |
|     1 |       |       |
+-------+-------+-------+
| 2     |   5 9 |       |
|   8   |       | 1   4 |
|       |       |       |
+-------+-------+-------+
| 5 3   |       |   9   |
|       | 4     | 6     |
|       |       |       |
+-------+-------+-------+ 
"""
        self.__test_that_search_leads_to_timeout(puzzle)


    def __test_that_search_leads_to_timeout(self, puzzle):
        for algorithm in ["Naive-DFS", "Naive-BFS", "Smart-DFS", "Smart-BFS"]:
            with self.subTest(algorithm = algorithm):
                search_summary, _ = TestSearchEngine.find_solution(puzzle, algorithm, timeout_sec = 1)
                self.assertEqual(SearchOutcome.TIMEOUT, search_summary.outcome)


class AbstractDeadEndTests(TestCase):
    """
    Base class providing functionality common to test fixtures covering the case when the attempt
    to solve a puzzle leads to dead end.
    """

    def verify_that_search_leads_to_expected_outcome(self, puzzle, expected_final_grid = None):
        for algorithm in self.algorithms:
            with self.subTest(algorithm = algorithm):
                search_summary, actual_final_grid = TestSearchEngine.find_solution(puzzle, algorithm, 20)
                self.assertEqual(self.expected_outcome, search_summary.outcome)
                self.__assertEquivalent(expected_final_grid, actual_final_grid)


    def __assertEquivalent(self, expected_output, actual_output):
        if expected_output is None:
            return
        expected_output = expected_output.strip()
        actual_output = actual_output.strip()
        self.assertEqual(expected_output, actual_output)


class PuzzleDeadEndTests(AbstractDeadEndTests):
    """
    Collection of integration tests covering the case when the search leads to puzzle
    dead end.
    """

    @property
    def algorithms(self):
        return ["UCS", "Smart-BFS", "Naive-BFS", "Smart-DFS", "Naive-DFS"]


    @property
    def expected_outcome(self):
        return SearchOutcome.PUZZLE_DEAD_END


    def test_puzzle_with_empty_cell_for_which_all_cell_values_are_excluded_by_row_and_column_puzzle_dead_end(self):
        puzzle = """
+-------+-------+-------+
| 1   7 |   2   | 9   4 |
|       |       |       |
|       |       |       |
+-------+-------+-------+
|       | 3     |       |
|       | 8     |       |
|       |       |       |
+-------+-------+-------+
|       | 6     |       |
|       |       |       |
|       | 5     |       |
+-------+-------+-------+ 
"""
        self.verify_that_search_leads_to_expected_outcome(puzzle, expected_final_grid = puzzle)


    def test_puzzle_with_empty_cell_for_which_all_cell_values_are_excluded_by_row_and_region_puzzle_dead_end(self):
        puzzle = """
+-------+-------+-------+
|       |       |       |
|       |       |       |
|       |       |       |
+-------+-------+-------+
| 7   5 | 3   9 |   1 2 |
|       | 8   4 |       |
|       | 6 5   |       |
+-------+-------+-------+
|       |       |       |
|       |       |       |
|       |       |       |
+-------+-------+-------+ 
"""
        self.verify_that_search_leads_to_expected_outcome(puzzle, expected_final_grid = puzzle)


    def test_puzzle_with_empty_cell_for_which_all_cell_values_are_excluded_by_column_and_region_puzzle_dead_end(self):
        puzzle = """
+-------+-------+-------+
|       |       |       |
|       |       | 6     |
|       |       | 3     |
+-------+-------+-------+
|       |       | 9     |
|       |       |       |
|       |       | 1     |
+-------+-------+-------+
|       |       |       |
|       |       | 2   4 |
|       |       | 5 7 8 |
+-------+-------+-------+ 
"""
        self.verify_that_search_leads_to_expected_outcome(puzzle, expected_final_grid = puzzle)


class AlgorithmDeadEnd(AbstractDeadEndTests):
    """
    Collection of integration tests covering the case when the search leads to
    algorithm dead end.
    """

    @property
    def algorithms(self):
        return ["UCS"]


    @property
    def expected_outcome(self):
        return SearchOutcome.ALGORITHM_DEAD_END


    def test_case_01(self):
        puzzle = """
+-------+-------+-------+
|   7 6 |   3 9 | 4 8 5 |
| 1     |       |       |
| 3     |     7 |       |
+-------+-------+-------+
| 8     |     5 |   4 9 |
| 6     |     3 | 2 7 8 |
| 5     |       |       |
+-------+-------+-------+
| 9     |     2 |       |
| 4     |     8 |       |
| 7     |     4 |       |
+-------+-------+-------+
"""
        expected_final_grid = """
+-------+-------+-------+
| 2 7 6 | 1 3 9 | 4 8 5 |
| 1     |     6 |       |
| 3     |     7 |       |
+-------+-------+-------+
| 8     |     5 | 1 4 9 |
| 6     |     3 | 2 7 8 |
| 5     |     1 |       |
+-------+-------+-------+
| 9     |     2 |     4 |
| 4     |     8 |       |
| 7     |     4 |       |
+-------+-------+-------+
"""
        self.verify_that_search_leads_to_expected_outcome(puzzle, expected_final_grid)


    def test_case_02(self):
        puzzle = """
+-------+-------+-------+
|       | 4   6 | 5     |
| 1     | 5   8 |     9 |
|       |   9   |       |
+-------+-------+-------+
|       |   6 5 |   9 1 |
|       |   8   | 3     |
|       | 1     |   5 2 |
+-------+-------+-------+
|   5   | 3   4 | 2   8 |
| 6     |       |     4 |
| 4   8 |       |   1   |
+-------+-------+-------+
"""
        expected_final_grid = """
+-------+-------+-------+
|       | 4 1 6 | 5     |
| 1     | 5 3 8 |     9 |
|       |   9   | 1     |
+-------+-------+-------+
|       |   6 5 |   9 1 |
|   1   | 9 8   | 3     |
|       | 1 4 3 |   5 2 |
+-------+-------+-------+
| 9 5 1 | 3 7 4 | 2 6 8 |
| 6     | 8 5 1 | 9 3 4 |
| 4 3 8 | 6 2 9 | 7 1 5 |
+-------+-------+-------+
"""
        self.verify_that_search_leads_to_expected_outcome(puzzle, expected_final_grid)


    def test_case_03(self):
        puzzle = """
+-------+-------+-------+
|       |     4 | 6     |
|       |   8   |     4 |
| 7 4   |   6   | 1     |
+-------+-------+-------+
|   8   | 5     |       |
| 1 9 6 |       | 7 3 5 |
|       |     6 |   2   |
+-------+-------+-------+
|     8 |   9   |   4 2 |
| 5     |   7   |       |
|     1 | 3     |       |
+-------+-------+-------+
"""
        expected_final_grid = """
+-------+-------+-------+
| 8     |     4 | 6     |
|       |   8   | 2   4 |
| 7 4   |   6   | 1     |
+-------+-------+-------+
|   8   | 5     |       |
| 1 9 6 |       | 7 3 5 |
|       |     6 |   2   |
+-------+-------+-------+
|     8 |   9   |   4 2 |
| 5     |   7   |       |
|     1 | 3     |       |
+-------+-------+-------+
"""
        self.verify_that_search_leads_to_expected_outcome(puzzle, expected_final_grid)


    def test_case_04(self):
        puzzle = """
+-------+-------+-------+
|       |       | 4     |
|       |       |       |
|       |     4 |       |
+-------+-------+-------+
|       | 7 1   |       |
|   4   |       |       |
|       |   8   |       |
+-------+-------+-------+
|     4 |       |       |
|       |       |       |
|       |       |     4 |
+-------+-------+-------+
"""
        expected_final_grid = """
+-------+-------+-------+
|       |       | 4     |
| 4     |       |       |
|       |     4 |       |
+-------+-------+-------+
|       | 7 1   |   4   |
|   4   |       |       |
|       | 4 8   |       |
+-------+-------+-------+
|     4 |       |       |
|       |   4   |       |
|       |       |     4 |
+-------+-------+-------+
"""
        self.verify_that_search_leads_to_expected_outcome(puzzle, expected_final_grid)


    def test_case_05(self):
        puzzle = """
+-------+-------+-------+
|       |     9 |       |
|       |       |       |
|       |       | 9     |
+-------+-------+-------+
|       |       |   5 9 |
|       |   5   |       |
| 3 9   |       |       |
+-------+-------+-------+
|     9 |       |   1   |
|       |       |   4   |
|       |       |       |
+-------+-------+-------+
"""
        expected_final_grid = """
+-------+-------+-------+
|       |     9 |       |
| 9     |       |       |
|       |       | 9     |
+-------+-------+-------+
|       |       |   5 9 |
|       | 9 5   |       |
| 3 9 5 |       |       |
+-------+-------+-------+
|     9 |       |   1   |
|       |   9   |   4   |
|       |       |   9   |
+-------+-------+-------+
"""
        self.verify_that_search_leads_to_expected_outcome(puzzle, expected_final_grid)


    def test_case_06(self):
        puzzle = """
+-------+-------+-------+
|       |       |   7 2 |
| 1     |       |       |
| 7     |     2 |       |
+-------+-------+-------+
|       | 7     |   1 5 |
|     2 |       |       |
|       |     5 |     7 |
+-------+-------+-------+
|   5 7 |       | 2     |
|       |       |       |
|       |     7 |       |
+-------+-------+-------+
"""
        expected_final_grid = """
+-------+-------+-------+
|       |       |   7 2 |
| 1 2   |   7   |       |
| 7     |     2 |       |
+-------+-------+-------+
|       | 7 2   |   1 5 |
| 5 7 2 |       |       |
|       |     5 |   2 7 |
+-------+-------+-------+
|   5 7 |       | 2     |
|       |       | 7     |
|       |     7 |       |
+-------+-------+-------+
"""
        self.verify_that_search_leads_to_expected_outcome(puzzle, expected_final_grid)


    def test_case_07(self):
        puzzle = """
+-------+-------+-------+
| 1     |       |       |
|   2   |       |       |
|     3 |       |       |
+-------+-------+-------+
|       | 4     |       |
|       |   5   |       |
|       |     6 |       |
+-------+-------+-------+
|       |       | 7     |
|       |       |   8   |
|       |       |     9 |
+-------+-------+-------+
"""
        expected_final_grid = """
+-------+-------+-------+
| 1     |       |       |
|   2   |       |       |
|     3 |       |       |
+-------+-------+-------+
|       | 4     |       |
|       |   5   |       |
|       |     6 |       |
+-------+-------+-------+
|       |       | 7     |
|       |       |   8   |
|       |       |     9 |
+-------+-------+-------+
"""
        self.verify_that_search_leads_to_expected_outcome(puzzle, expected_final_grid)


class ErrorTests(TestCase):
    """
    Collection of integration tests covering the case when a puzzle is rejected by the search
    engine, for instance if it is an invalid puzzle, or if the puzzle does not contain any empty
    cell.
    """

    def test_invalid_search_algorithm_specified_exception_raised(self):
        puzzle = """
+-------+-------+-------+
| 6     |     4 |   8 5 |
| 9 7   |   6 5 |       |
|   4 8 | 7 3   |       |
+-------+-------+-------+
|   8   | 2 4 7 |       |
|     6 |   8   | 5     |
|       | 1 5 6 |   4   |
+-------+-------+-------+
|       |   1 3 | 2 6   |
|       | 6 9   |   3 4 |
| 2 6   | 4     |     9 |
+-------+-------+-------+
"""
        with self.assertRaises(NoSuchAlgorithmError):
            TestSearchEngine.find_solution(puzzle, "NO-SUCH-ALGORITHM")


    def test_invalid_puzzle_duplicate_value_in_a_validation_block_exception_raised(self):
        invalid_puzzle = """
+-------+-------+-------+
|       |       |       |
|       |       |       |
|       |       |       |
+-------+-------+-------+
|       |       |       |
| 1   7 |   2   | 7   4 |
|       |       |       |
+-------+-------+-------+
|       |       |       |
|       |       |       |
|       |       |       |
+-------+-------+-------+ 
"""
        with self.assertRaises(InvalidPuzzleError):
            TestSearchEngine.find_solution(invalid_puzzle, "Smart-DFS")


    def test_puzzle_without_empty_cell_exception_raised(self):
        invalid_puzzle = """
+-------+-------+-------+
| 6 3 1 | 9 2 4 | 7 8 5 |
| 9 7 2 | 8 6 5 | 4 1 3 |
| 5 4 8 | 7 3 1 | 9 2 6 |
+-------+-------+-------+
| 3 8 5 | 2 4 7 | 6 9 1 |
| 4 1 6 | 3 8 9 | 5 7 2 |
| 7 2 9 | 1 5 6 | 3 4 8 |
+-------+-------+-------+
| 8 9 4 | 5 1 3 | 2 6 7 |
| 1 5 7 | 6 9 2 | 8 3 4 |
| 2 6 3 | 4 7 8 | 1 5 9 |
+-------+-------+-------+
"""
        with self.assertRaises(InvalidPuzzleError):
            TestSearchEngine.find_solution(invalid_puzzle, "Smart-BFS")


basicConfig(level = INFO,
        format = "%(asctime)s %(levelname)-8s %(module)-18s line %(lineno)-4d %(message)s",
        datefmt = "%d-%b-%Y %H:%M:%S",
        filename = "integrationtests.log",
        filemode = "w")
