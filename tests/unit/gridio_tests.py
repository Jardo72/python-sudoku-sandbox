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
This module is a collection of unit tests aimed at the classes provided by the gridio
module.
"""

from unittest import TestCase

from grid import Grid
from gridio import PuzzleParser, GridFormatter, InvalidInputError

_ = None

class PuzzleParserTest(TestCase):
    """
    Collection of unit tests exercising the gridio.PuzzleParser class.
    """

    def test_valid_input_with_proper_cell_values_returned(self):
        valid_input = """
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
        expected_cell_values = [
            [ 6, _, _, _, _, 4, _, 8, 5 ],
            [ 9, 7, _, _, 6, 5, _, _, _ ],
            [ _, 4, 8, 7, 3, _, _, _, _ ],
            [ _, 8, _, 2, 4, 7, _, _, _ ],
            [ _, _, 6, _, 8, _, 5, _, _ ],
            [ _, _, _, 1, 5, 6, _, 4, _ ],
            [ _, _, _, _, 1, 3, 2, 6, _ ],
            [ _, _, _, 6, 9, _, _, 3, 4 ],
            [ 2, 6, _, 4, _, _, _, _, 9 ],
        ]
        actual_cell_values = PuzzleParser.read_from_string(valid_input)
        self.assertEqual(expected_cell_values, actual_cell_values)


    def test_valid_input_with_leading_and_trailing_whitespace_proper_cell_values_returned(self):
        valid_input = """
            +-------+-------+-------+
            | 3     |     4 |   9   |   
            | 1     |   6 5 |       |
            |     7 |   2   |       |
            +-------+-------+-------+   
            |   8   |   1 3 |       |
            |     6 |   8   | 5     |
            |       | 5   6 |   4   |
            +-------+-------+-------+
            |       |   1   | 4 6   |
            |       | 6 9   |   2   |
            | 2 7   | 4     |     9 |
            +-------+-------+-------+
"""
        expected_cell_values = [
            [ 3, _, _, _, _, 4, _, 9, _ ],
            [ 1, _, _, _, 6, 5, _, _, _ ],
            [ _, _, 7, _, 2, _, _, _, _ ],
            [ _, 8, _, _, 1, 3, _, _, _ ],
            [ _, _, 6, _, 8, _, 5, _, _ ],
            [ _, _, _, 5, _, 6, _, 4, _ ],
            [ _, _, _, _, 1, _, 4, 6, _ ],
            [ _, _, _, 6, 9, _, _, 2, _ ],
            [ 2, 7, _, 4, _, _, _, _, 9 ],
        ]
        actual_cell_values = PuzzleParser.read_from_string(valid_input)
        self.assertEqual(expected_cell_values, actual_cell_values)


    def test_letter_as_cell_value_exception_raised(self):
        invalid_input = """
+-------+-------+-------+
| 6     |     4 |   8 5 |
| 9 7   |   6 5 |       |
|   4 8 | 7 x   |       |
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
        with self.assertRaises(InvalidInputError):
            PuzzleParser.read_from_string(invalid_input)


    def test_special_character_as_cell_value_exception_raised(self):
        invalid_input = """
+-------+-------+-------+
| 3     |       |   8 5 |
|   9   |   6 1 |       |
|   8 4 |   $   |       |
+-------+-------+-------+
|   4   | 2     |       |
|     6 |       | 5     |
|       | 1     |   4   |
+-------+-------+-------+
|       |   1   | 6     |
|       | 6     |   3   |
| 2 6   | 4     |     1 |
+-------+-------+-------+ 
"""
        with self.assertRaises(InvalidInputError):
            PuzzleParser.read_from_string(invalid_input)


    def test_zero_as_cell_value_exception_raised(self):
        invalid_input = """
+-------+-------+-------+
| 1     |       |       |
|   5   |     9 |       |
|       |       | 2     |
+-------+-------+-------+
|   0   |       |       |
|       |       |   1   |
|       |   7   |       |
+-------+-------+-------+
|       |       | 6   4 |
|       |       | 8     |
|     4 |       |     3 |
+-------+-------+-------+ 
"""
        with self.assertRaises(InvalidInputError):
            PuzzleParser.read_from_string(invalid_input)


    def test_invalid_border_exception_raised(self):
        invalid_input = """
+-------+-------+-------+
| 1     |       |       |
|   5   |     9 |       |
|       |       | 2     |
+-------+--
|   1   |       |       |
|       |       |   1   |
| 3     |   7   |       |
+-------+-------+-------+
|       |       | 6   4 |
|       |       | 8     |
|     4 |       |     3 |
+-------+-------+-------+ 
"""
        with self.assertRaises(InvalidInputError):
            PuzzleParser.read_from_string(invalid_input)


    def test_grid_with_missing_lines_exception_raised(self):
        invalid_input = """
+-------+-------+-------+
| 1     |       |       |
|   5   |     9 |       |
|       |       | 2     |
+-------+-------+-------+
|   1   |       |       |
|       |       |   1   |
| 3     |   7   |       |
+-------+-------+-------+
"""
        with self.assertRaises(InvalidInputError):
            PuzzleParser.read_from_string(invalid_input)


    def test_empty_input_exception_raised(self):
        invalid_input = ""
        with self.assertRaises(InvalidInputError):
            PuzzleParser.read_from_string(invalid_input)


class GridFormatterTest(TestCase):
    """
    Collection of unit tests exercising the gridio.GridFormatter class.
    """

    def test_empty_grid_is_formatted_properly(self):
        cell_values = [
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
        ]

        expected_output = """
+-------+-------+-------+
|       |       |       |
|       |       |       |
|       |       |       |
+-------+-------+-------+
|       |       |       |
|       |       |       |
|       |       |       |
+-------+-------+-------+
|       |       |       |
|       |       |       |
|       |       |       |
+-------+-------+-------+ 
"""
        grid = Grid(cell_values)
        actual_output = GridFormatter.write_to_string(grid)
        self.__assertEquivalent(expected_output, actual_output)


    def test_incomplete_grid_is_formatted_properly(self):
        cell_values = [
            [ 6, _, _, _, _, 4, _, 8, 5 ],
            [ 9, 7, _, _, 6, 5, _, _, _ ],
            [ _, 4, 8, 7, 3, _, _, _, _ ],
            [ _, 8, _, 2, 4, 7, _, _, _ ],
            [ _, _, 6, _, 8, _, 5, _, _ ],
            [ _, _, _, 1, 5, 6, _, 4, _ ],
            [ _, _, _, _, 1, 3, 2, 6, _ ],
            [ _, _, _, 6, 9, _, _, 3, 4 ],
            [ 2, 6, _, 4, _, _, _, _, 9 ],
        ]

        expected_output = """
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
        grid = Grid(cell_values)
        actual_output = GridFormatter.write_to_string(grid)
        self.__assertEquivalent(expected_output, actual_output)


    def test_complete_grid_is_formatted_properly(self):
        cell_values = [
            [ 6, 3, 1, 9, 2, 4, 7, 8, 5 ],
            [ 9, 7, 2, 8, 6, 5, 4, 1, 3 ],
            [ 5, 4, 8, 7, 3, 1, 9, 2, 6 ],
            [ 3, 8, 5, 2, 4, 7, 6, 9, 1 ],
            [ 4, 1, 6, 3, 8, 9, 5, 7, 2 ],
            [ 7, 2, 9, 1, 5, 6, 3, 4, 8 ],
            [ 8, 9, 4, 5, 1, 3, 2, 6, 7 ],
            [ 1, 5, 7, 6, 9, 2, 8, 3, 4 ],
            [ 2, 6, 3, 4, 7, 8, 1, 5, 9 ],
        ]

        expected_output = """
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
        grid = Grid(cell_values)
        actual_output = GridFormatter.write_to_string(grid)
        self.__assertEquivalent(expected_output, actual_output)


    def __assertEquivalent(self, expected_output, actual_output):
        expected_output = expected_output.strip()
        actual_output = actual_output.strip()
        self.assertEqual(expected_output, actual_output)
