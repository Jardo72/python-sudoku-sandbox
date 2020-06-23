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
This module provides an object-oriented representation of Sudoku grid. Besides the Grid
class, this module also provides:
* other type(s) participating on the public API provided by the Grid class
* supporting functionality participating on the internal implementation of the Grid class
"""

from collections import Counter, namedtuple
from enum import Enum, unique
from logging import getLogger
from typing import Optional, Sequence, Tuple

_logger = getLogger()

@unique
class CellStatus(Enum):
    """
    Defines possible states of a single cell within a Sudoku grid. The meaning of
    particular enum elements is the following:
    * UNDEFINED indicates that a cell has no value (i.e. it was not defined in the
      original puzzle, and it has not been completed yet.
    * PREDEFINED indicates that a call was already defined in the original puzzle.
    * COMPLETED indicates that a call was undefined in the original puzzle, but it
      has been completed in the meantime (i.e. it has already a value).
    """

    UNDEFINED = 1

    PREDEFINED = 2

    COMPLETED = 3


class _ValidationBlocks:
    """
    Internal helper class supporting the validation of grid by defining validation blocks.
    A validation block is formed by cells that belong to a single row, or to a single column,
    or to a single region.
    """

    @staticmethod
    def create():
        rows = [tuple([(row, column) for column in range(0, 9)]) for row in range(0, 9)]
        columns = [tuple([(row, column) for row in range(0, 9)]) for column in range(0, 9)]
        regions = [_ValidationBlocks.__single_region(topmost_row, leftmost_column) for topmost_row in [0, 3, 6] for leftmost_column in [0, 3, 6]]
        return tuple(rows + columns + regions)


    @staticmethod
    def __single_region(topmost_row: int, leftmost_column: int) -> Tuple[Tuple[int, int], ...]:
        result = [(row, column) for row in range(topmost_row, topmost_row + 3) for column in range(leftmost_column, leftmost_column + 3)]
        return tuple(result)


_Cell = namedtuple("Cell", ["value", "status"])

class Grid:
    """
    Object-oriented representation of Sudoku grid. Besides the cell values, this grid also keeps
    track of the status of each cell, so it is able to distinguish whether a cell is empty (i.e.
    undefined), if it was predefined (i.e. its value was defined by the original puzzle), or if
    its value has been completed during the search (i.e. it was not predefined, but it is not
    empty anymore). In order to prevent excessive memory consumption and time-consuming cloning
    of grids, an immutable singleton is used to represent each combination of status and value.
    In concrete terms, there are 9 singletons for predefined cells, 9 singletons for completed
    cells, plus one singleton for undefined cell. An unlimited number of grids can safely share
    these singleton objects to represent their cells. Cloning of a grid does not have to clone
    the objects representing the cells, it is enough to clone the collection containing the
    cell objects.
    """

    __cell_addresses = tuple([(row, column) for row in range(0, 9) for column in range(0, 9)])

    __undefined_cell = _Cell(None, CellStatus.UNDEFINED)

    __predefined_cells = {value: _Cell(value, CellStatus.PREDEFINED) for value in range(1, 10)}

    __completed_cells = {value: _Cell(value, CellStatus.COMPLETED) for value in range(1, 10)}

    __validation_blocks = _ValidationBlocks.create()


    def __init__(self, cell_values: Optional[Sequence[Sequence[Optional[int]]]] = None,
                 original = None):
        """
        Initializer allowing to create a new Grid either using the given cell values, or as
        a clone of the given grid. In any of the two cases, use only one of the two arguments
        - the other must be None.

        Args:
            cell_values:    A list of lists, where the nested lists represent rows of the grid.
                            Single value in such a nested list is either an int representing the
                            cell value, or None in case of undefined value. Use this parameter
                            if you want to create a new grid with the given cell values. If you
                            want to create a copy of an existing grid, use None.
            original:       Original grid that is to be cloned. Use None if you want to create
                            a new grid based on list with cell values.

        Raises:
            ValueError:     If both parameters are None, or if both parameters are not None.
        """
        if Grid.__is_ordinary_constructor(cell_values, original):
            self._cells, self._undefined_cell_count = Grid.__create_from_cell_values(cell_values)
        elif Grid.__is_copy_constructor(cell_values, original):
            self._cells = [original._cells[row].copy() for row in range(0, 9)]
            self._undefined_cell_count = original._undefined_cell_count
        else:
            message = "Invalid arguments. Exactly one of the two arguments is expected."
            raise ValueError(message)


    @staticmethod
    def __is_ordinary_constructor(cell_values, original) -> bool:
        return original is None and isinstance(cell_values, list)


    @staticmethod
    def __is_copy_constructor(cell_values, original) -> bool:
        return cell_values is None and isinstance(original, Grid)


    @staticmethod
    def __create_from_cell_values(cell_values):
        cells = []
        undefined_cell_count = 9 * 9
        for row in range(0, 9):
            row_cells = []
            for column in range(0, 9):
                cell = Grid.__convert_to_cell(cell_values, row, column)
                if cell.status is not CellStatus.UNDEFINED:
                    undefined_cell_count -= 1
                row_cells.append(cell)
            cells.append(row_cells)
        return (cells, undefined_cell_count)


    @staticmethod
    def __convert_to_cell(cell_values, row: int, column: int) -> _Cell:
        if (cell_values[row][column] is None):
            return Grid.__undefined_cell
        return Grid.__predefined_cells[cell_values[row][column]]


    @staticmethod
    def get_all_cell_addresses() -> Tuple[Tuple[int, int], ...]:
        """
        Returns a tuple containing addresses of all 81 cells comprising the grid. Each address
        is represented by a tuple with two elements. The first element represents teh row, the
        second element represents the column.
        """
        return Grid.__cell_addresses


    def get_undefined_cell_count(self) -> int:
        """
        Returns the number of undefined cells within this grid.

        Returns:
            The number of cells contained within this grid whose values have not been
            defined yet.
        """
        return self._undefined_cell_count


    def get_cell_value(self, row: int, column: int) -> int:
        """
        Returns the value of the cell with the given coordinates.

        Args:
            row (int):      The row coordinate of the cell whose value is to
                            be returned. Zero corresponds to the first row,
                            eight corresponds to the last row.
            column (int):   The column coordinate of the cell whose value is to
                            be returned. Zero corresponds to the first column,
                            eight corresponds to the last column.

        Returns (int):
            The value of the desired cell, or None if the desired cell is
            undefined.
        """
        return self._cells[row][column].value


    def get_cell_status(self, row: int, column: int) -> CellStatus:
        """
        Returns the status of the cell with the given coordinates.

        Args:
            row (int):      The row coordinate of the cell whose status is to
                            be returned. Zero corresponds to the first row,
                            eight corresponds to the last row.
            column (int):   The column coordinate of the cell whose status is to
                            be returned. Zero corresponds to the first column,
                            eight corresponds to the last column.

        Returns (CellStatus):
            The status of the desired cell represented by one of the CellStatus enum
            elements.
        """
        return self._cells[row][column].status


    def is_valid(self) -> bool:
        """
        Verifies whether this grid is valid. An incomplete grid (i.e. grid with at least
        one undefined cell) is also valid if it does not violate the Sudoku rules.

        Returns:
            True if and only if none of the rows, columns and regions of this grid
            contains a duplicate value; False if this grid contains at least one row,
            column, or region containing at least one duplicate value.
        """
        for single_validation_block in Grid.__validation_blocks:
            if not self.__is_valid_block(single_validation_block):
                return False
        return True


    def __is_valid_block(self, block) -> bool:
        counter: Counter = Counter()
        for cell_address in block:
            row, column = cell_address
            cell_value = self._cells[row][column].value
            if cell_value is not None:
                counter[cell_value] += 1

        most_common = counter.most_common(1)
        if len(most_common) != 0 and most_common[0][1] > 1:
            _logger.error("The value %d is present %dx in the validation block %s", most_common[0][0], most_common[0][1], block)
            return False
        return True


    def is_complete(self) -> bool:
        """
        Verifies whether each and every cell contained in this grid has a value.
        This method does not care about validity. In other words, a grid without
        any empty cell is considered complete even if two cells within a row,
        column or region contain the same value.

        Returns:
            True if and only if none of the cells of this grid is empty; False if
            this grid contains at least one empty value.
        """
        return self._undefined_cell_count == 0


    def set_cell_value(self, row: int, column: int, value: int):
        """
        Sets the cell with the given coordinates to the given value, assumed the
        cell with the given coordinates is empty (i.e. its value is undefined).

        Args:
            row (int):      The row coordinate of the cell whose value is to
                            be set. Zero corresponds to the first row, eight
                            corresponds to the last row.
            column (int)    The column coordinate of the cell whose value is to
                            be set. Zero corresponds to the first column, eight
                            corresponds to the last column.
            value (int):    The new value for the given cell.

        Raises:
            ValueError      If the given cell has already a value, regardless
                            of whether the value was defined in the original
                            puzzle or completed during the search.
        """
        _logger.debug("Going to set the value of cell [%d, %d] to %d", row, column, value)
        cell = self._cells[row][column]
        if cell.status is not CellStatus.UNDEFINED:
            _logger.error("Cell [%d, %d] not empty (status = %s), going to raise an error", row, column, cell.status)
            message = "Cannot modify the cell [{0}, {1}] as its state is {2} (current cell value = {3}, value to be set = {4})."
            raise ValueError(message.format(row, column, cell.status, cell.value, value))
        self._cells[row][column] = Grid.__completed_cells[value]
        self._undefined_cell_count -= 1


    def copy(self):
        """
        Creates and returns a copy of this grid which behaves as if it was a deep copy
        of this grid.

        Returns:
            The created clone of this grid. Be aware of the fact that the returned
            grid is semantically equivalent to deep copy of this grid. In other words,
            any modification of the clone will not change the status of this grid and
            vice versa.
        """
        return Grid(original = self)
