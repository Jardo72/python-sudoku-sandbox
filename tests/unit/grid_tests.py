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
This module is a collection of unit tests covering the functionality provided by the grid module.
"""

from unittest import TestCase

from grid import Grid, CellStatus

_ = None

class GridValidityTest(TestCase):
    """
    Test fixture covering verification of the validity of a Sudoku grid. In order to achieve
    reasonable balance between the number of test cases and the defect detection ability, test
    cases aimed at invalid grid cover:
    * all edge validation blocks, i.e. the first and the last row, the first and the last
      column, and the regions in all four corners of the grid
    * as many of the nine valid cell values as possible with the number of test cases
      implied by the item above (i.e. 8 cell values are covered, including the edge values
      1 and 9)
    """

    def test_incomplete_grid_without_violation_is_valid(self):
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
        grid = Grid(cell_values)
        self.assertTrue(grid.is_valid())


    def test_complete_grid_without_violation_is_valid(self):
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
        grid = Grid(cell_values)
        self.assertTrue(grid.is_valid())


    def test_incomplete_grid_with_duplicate_in_first_row_is_invalid(self):
        cell_values = [
            [ 1, _, 7, _, 2, _, 7, _, 4 ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
        ]
        grid = Grid(cell_values)
        self.assertFalse(grid.is_valid())


    def test_incomplete_grid_with_duplicate_in_last_row_is_invalid(self):
        cell_values = [
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, 2, 8, 3, 2, _, 7, _, 1 ],
        ]
        grid = Grid(cell_values)
        self.assertFalse(grid.is_valid())


    def test_incomplete_grid_with_duplicate_in_first_column_is_invalid(self):
        cell_values = [
            [ 1, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ 7, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ 4, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ 1, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ 6, _, _, _, _, _, _, _, _ ],
        ]
        grid = Grid(cell_values)
        self.assertFalse(grid.is_valid())


    def test_incomplete_grid_with_duplicate_in_last_column_is_invalid(self):
        cell_values = [
            [ _, _, _, _, _, _, _, _, 3 ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, 6 ],
            [ _, _, _, _, _, _, _, _, 9 ],
            [ _, _, _, _, _, _, _, _, 2 ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, 6 ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, 1 ],
        ]
        grid = Grid(cell_values)
        self.assertFalse(grid.is_valid())


    def test_incomplete_grid_with_duplicate_in_upper_left_region_is_invalid(self):
        cell_values = [
            [ 4, 1, _, _, _, _, _, _, _ ],
            [ 7, _, _, _, _, _, _, _, _ ],
            [ _, _, 4, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
        ]
        grid = Grid(cell_values)
        self.assertFalse(grid.is_valid())


    def test_incomplete_grid_with_duplicate_in_bottom_left_region_is_invalid(self):
        cell_values = [
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ 7, _, 2, _, _, _, _, _, _ ],
            [ _, 5, _, _, _, _, _, _, _ ],
            [ 3, _, 5, _, _, _, _, _, _ ],
        ]
        grid = Grid(cell_values)
        self.assertFalse(grid.is_valid())


    def test_incomplete_grid_with_duplicate_in_upper_right_region_is_invalid(self):
        cell_values = [
            [ _, _, _, _, _, _, _, _, 9 ],
            [ _, _, _, _, _, _, _, 2, _ ],
            [ _, _, _, _, _, _, 9, _, 7 ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
        ]
        grid = Grid(cell_values)
        self.assertFalse(grid.is_valid())


    def test_incomplete_grid_with_duplicate_in_bottom_right_region_is_invalid(self):
        cell_values = [
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, 6, _, 4 ],
            [ _, _, _, _, _, _, 8, _, _ ],
            [ _, _, _, _, _, _, _, 8, 3 ],
        ]
        grid = Grid(cell_values)
        self.assertFalse(grid.is_valid())


class GridCompletnessTest(TestCase):
    """
    Test fixture covering verification of the completness of a Sudoku grid.
    """

    def test_valid_grid_without_empty_cell_is_complete(self):
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
        grid = Grid(cell_values)
        self.assertTrue(grid.is_complete())


    def test_valid_grid_with_empty_cell_in_first_row_is_incomplete(self):
        cell_values = [
            [ 6, 3, _, 9, 2, 4, 7, 8, 5 ],
            [ 9, 7, 2, 8, 6, 5, 4, 1, 3 ],
            [ 5, 4, 8, 7, 3, 1, 9, 2, 6 ],
            [ 3, 8, 5, 2, 4, 7, 6, 9, 1 ],
            [ 4, 1, 6, 3, 8, 9, 5, 7, 2 ],
            [ 7, 2, 9, 1, 5, 6, 3, 4, 8 ],
            [ 8, 9, 4, 5, 1, 3, 2, 6, 7 ],
            [ 1, 5, 7, 6, 9, 2, 8, 3, 4 ],
            [ 2, 6, 3, 4, 7, 8, 1, 5, 9 ],
        ]
        grid = Grid(cell_values)
        self.assertFalse(grid.is_complete())


    def test_valid_grid_with_empty_cell_in_last_row_is_incomplete(self):
        cell_values = [
            [ 6, 3, 1, 9, 2, 4, 7, 8, 5 ],
            [ 9, 7, 2, 8, 6, 5, 4, 1, 3 ],
            [ 5, 4, 8, 7, 3, 1, 9, 2, 6 ],
            [ 3, 8, 5, 2, 4, 7, 6, 9, 1 ],
            [ 4, 1, 6, 3, 8, 9, 5, 7, 2 ],
            [ 7, 2, 9, 1, 5, 6, 3, 4, 8 ],
            [ 8, 9, 4, 5, 1, 3, 2, 6, 7 ],
            [ 1, 5, 7, 6, 9, 2, 8, 3, 4 ],
            [ 2, 6, 3, 4, 7, _, 1, 5, 9 ],
        ]
        grid = Grid(cell_values)
        self.assertFalse(grid.is_complete())


    def test_valid_grid_with_empty_cell_in_first_column_is_incomplete(self):
        cell_values = [
            [ 6, 3, 1, 9, 2, 4, 7, 8, 5 ],
            [ 9, 7, 2, 8, 6, 5, 4, 1, 3 ],
            [ _, 4, 8, 7, 3, 1, 9, 2, 6 ],
            [ 3, 8, 5, 2, 4, 7, 6, 9, 1 ],
            [ 4, 1, 6, 3, 8, 9, 5, 7, 2 ],
            [ 7, 2, 9, 1, 5, 6, 3, 4, 8 ],
            [ 8, 9, 4, 5, 1, 3, 2, 6, 7 ],
            [ 1, 5, 7, 6, 9, 2, 8, 3, 4 ],
            [ 2, 6, 3, 4, 7, 8, 1, 5, 9 ],
        ]
        grid = Grid(cell_values)
        self.assertFalse(grid.is_complete())


    def test_valid_grid_with_empty_cell_in_last_column_is_incomplete(self):
        cell_values = [
            [ 6, 3, 1, 9, 2, 4, 7, 8, 5 ],
            [ 9, 7, 2, 8, 6, 5, 4, 1, 3 ],
            [ 5, 4, 8, 7, 3, 1, 9, 2, 6 ],
            [ 3, 8, 5, 2, 4, 7, 6, 9, 1 ],
            [ 4, 1, 6, 3, 8, 9, 5, 7, _ ],
            [ 7, 2, 9, 1, 5, 6, 3, 4, 8 ],
            [ 8, 9, 4, 5, 1, 3, 2, 6, 7 ],
            [ 1, 5, 7, 6, 9, 2, 8, 3, 4 ],
            [ 2, 6, 3, 4, 7, 8, 1, 5, 9 ],
        ]
        grid = Grid(cell_values)
        self.assertFalse(grid.is_complete())


class GridUndefinedCellCountTest(TestCase):
    """
    Test fixture aimed at the Grid.get_undefined_cell_count method.
    """

    def test_empty_grid_has_eighty_one_undefined_cells(self):
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
        grid = Grid(cell_values)
        self.assertEqual(grid.get_undefined_cell_count(), 81)


    def test_incomplete_grid_has_proper_number_of_undefined_cells(self):
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
        grid = Grid(cell_values)
        self.assertEqual(grid.get_undefined_cell_count(), 46)

    def test_complete_grid_has_zero_undefined_cells(self):
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
        grid = Grid(cell_values)
        self.assertEqual(grid.get_undefined_cell_count(), 0)


    def test_undefined_cell_count_is_decreased_whenever_cell_is_completed(self):
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
        grid = Grid(cell_values)

        grid.set_cell_value(row = 0, column = 6, value = 1)
        self.assertEqual(grid.get_undefined_cell_count(), 45)

        grid.set_cell_value(row = 7, column = 0, value = 3)
        self.assertEqual(grid.get_undefined_cell_count(), 44)

        grid.set_cell_value(row = 4, column = 8, value = 7)
        self.assertEqual(grid.get_undefined_cell_count(), 43)


class GridCellManipulationTest(TestCase):
    """
    Test fixture aimed at the Grid.set_cell_value method.
    """

    def test_undefined_cells_have_proper_value_and_status(self):
        cell_values = [
            [ 1, _, _, _, _, _, _, _, 2 ],
            [ _, _, _, _, 8, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, 5, _, _, _, _, _ ],
            [ _, _, _, _, 6, _, _, _, _ ],
            [ _, _, _, _, _, 7, _, _, _ ],
            [ _, _, _, 9, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ 3, _, _, _, _, _, _, _, 4 ],
        ]
        grid = Grid(cell_values)

        cells_to_be_verified = [(0, 1), (1, 0), (0, 7), (1, 8), (7, 0), (8, 1), (7, 8), (8, 7), (5, 3), (3, 6), (6, 5)]
        for (row, column) in cells_to_be_verified:
            self.assertEqual(grid.get_cell_value(row, column), None)
            self.assertEqual(grid.get_cell_status(row, column), CellStatus.UNDEFINED)


    def test_predefined_cells_have_proper_value_and_status(self):
        cell_values = [
            [ 1, _, _, _, _, _, _, _, 2 ],
            [ _, _, _, _, 8, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, _, _, 5, _, _, _, _, _ ],
            [ _, _, _, _, 6, _, _, _, _ ],
            [ _, _, _, _, _, 7, _, _, _ ],
            [ _, _, _, 9, _, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ 3, _, _, _, _, _, _, _, 4 ],
        ]
        grid = Grid(cell_values)

        cell_list = [(0, 0, 1), (0, 8, 2), (8, 0, 3), (8, 8, 4), (1, 4, 8), (3, 3, 5), (4, 4, 6), (5, 5, 7), (6, 3, 9)]
        for (row, column, value) in cell_list:
            self.assertEqual(grid.get_cell_value(row, column), value)
            self.assertEqual(grid.get_cell_status(row, column), CellStatus.PREDEFINED)


    def test_completed_cells_have_proper_value_and_status(self):
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
        grid = Grid(cell_values)

        cell_list = [(0, 1, 3), (2, 8, 1), (5, 0, 7), (3, 6, 3), (8, 7, 5)]
        for (row, column, value) in cell_list:
            grid.set_cell_value(row, column, value)
            self.assertEqual(grid.get_cell_value(row, column), value)
            self.assertEqual(grid.get_cell_status(row, column), CellStatus.COMPLETED)


    def test_modification_of_predefined_cell_leads_to_exception(self):
        cell_values = [
            [ 4, 1, _, _, _, _, _, _, _ ],
            [ 7, _, _, _, _, _, _, _, _ ],
            [ _, _, 4, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, 3, _, _ ],
            [ _, _, _, _, 9, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, 1, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, 8, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
        ]
        grid = Grid(cell_values)

        cell_list = [(0, 0, 2), (0, 1, 3), (4, 4, 8), (3, 6, 9), (7, 6, 5)]
        for (row, column, value) in cell_list:
            with self.assertRaises(ValueError):
                grid.set_cell_value(row, column, value)

    
    def test_modification_of_completed_cell_leads_to_exception(self):
        cell_values = [
            [ 4, 1, _, _, _, _, _, _, _ ],
            [ 7, _, _, _, _, _, _, _, _ ],
            [ _, _, 4, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, 3, _, _ ],
            [ _, _, _, _, 9, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, 1, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, 8, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
        ]
        grid = Grid(cell_values)
        grid.set_cell_value(row = 1, column = 8, value = 2)

        with self.assertRaises(ValueError):
            grid.set_cell_value(row = 1, column = 8, value = 3)


class GridCloneTest(TestCase):
    """
    Test fixture verifying that cloning of Grid instances works properly.
    """

    def test_clone_has_the_same_cell_values_and_states_as_the_original_grid(self):
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
        original_grid = Grid(cell_values)
        clone = original_grid.copy()

        for row in range(0, 9):
            for column in range(0, 9):
                self.assertEqual(original_grid.get_cell_value(row, column), clone.get_cell_value(row, column))
                self.assertEqual(original_grid.get_cell_status(row, column), clone.get_cell_status(row, column))


    def test_modification_of_clone_does_not_change_original_grid(self):
        cell_values = [
            [ 4, 1, _, _, _, _, _, _, _ ],
            [ 7, _, _, _, _, _, _, _, _ ],
            [ _, _, 4, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, 3, _, _ ],
            [ _, _, _, _, 9, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, 1, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, 8, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
        ]
        original_grid = Grid(cell_values)
        clone = original_grid.copy()

        cell_list = [(0, 5, 6), (7, 0, 3), (3, 5, 2), (8, 8, 6)]
        for (row, column, value) in cell_list:
            clone.set_cell_value(row, column, value)
            self.assertEqual(original_grid.get_cell_value(row, column), None)
            self.assertEqual(original_grid.get_cell_status(row, column), CellStatus.UNDEFINED)


    def test_modification_of_original_grid_does_not_change_clone(self):
        cell_values = [
            [ 4, 1, _, _, _, _, _, _, _ ],
            [ 7, _, _, _, _, _, _, _, _ ],
            [ _, _, 4, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, 3, _, _ ],
            [ _, _, _, _, 9, _, _, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
            [ _, 1, _, _, _, _, _, _, _ ],
            [ _, _, _, _, _, _, 8, _, _ ],
            [ _, _, _, _, _, _, _, _, _ ],
        ]
        original_grid = Grid(cell_values)
        clone = original_grid.copy()

        cell_list = [(0, 5, 6), (7, 0, 3), (3, 3, 2), (5, 6, 6), (8, 5, 2)]
        for (row, column, value) in cell_list:
            original_grid.set_cell_value(row, column, value)
            self.assertEqual(clone.get_cell_value(row, column), None)
            self.assertEqual(clone.get_cell_status(row, column), CellStatus.UNDEFINED)


class GridOtherTest(TestCase):
    """
    Test fixture aimed at other (i.e. not covered by the test fixtures above) methods
    provided by the Grid class.
    """

    def test_get_all_cell_addresses(self):
        address_list = Grid.get_all_cell_addresses()
        for row in range(0, 9):
            for column in range(0, 9):
                message = "[{0}, {1}]".format(row, column)
                self.assertTrue((row, column) in address_list, message)