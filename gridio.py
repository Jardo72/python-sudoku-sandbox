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
This module provides classes allowing to:
* parse input files with puzzles
* and format final grids representing the outcome of a search.
"""

from io import StringIO
from sys import stdout
from typing import List, Optional

from grid import Grid, CellStatus


def _border_line_template() -> str:
    return "+-------+-------+-------+"


def _cell_line_template() -> str:
    return "| ? ? ? | ? ? ? | ? ? ? |"


class InvalidInputError(Exception):
    """
    Raised to inidicate that the class gridio.PuzzleParser has encountered an invalid
    input (regardless of whether a file or a string).
    """
    pass


class PuzzleParser:
    """
    Simple parser allowing to read and parse a textual representation of a puzzle
    from an input file or a string.

    Note:
        This class is not supposed to be directly instantiated by other classes.
        Instead, use the public static methods provided by this class. They are
        very easy to use, and they also take care about the proper release of
        resources like open files.
    """

    def __init__(self, input):
        """
        Internal initializer which is not to be used directly. Constructs a new parser
        that will parse the given input.

        Args:
            input:      The string to be parsed.
        """
        self._lines = [single_line.strip() for single_line in input.readlines()]


    @staticmethod
    def read_from_file(filename: str) -> List[List[int]]:
        """
        Reads the input file with the given filename and parses the textual representation
        of the grid contained in it.

        Agrs:
            filename:    The name of the input file to be read and parsed.
        
        Returns:         List of lists, where a single value in such a nested list
                         corresponds to a single cell from the parsed grid. The None value
                         is used for undefined cells, int values between 1 and 9 are used
                         for defined cells.

        Raises:
            InvalidInputError   If the given input is invalid (e.g. crippled grid, invalid
                                cell values etc.).
        """
        with open(filename, "r") as file:
            parser = PuzzleParser(file)
            return parser.__get_cells()


    @staticmethod
    def read_from_string(grid_as_string: str) -> List[List[int]]:
        """
        Reads and parses the given textual representation of a grid.

        Agrs:
            grid_as_string:    The textual representation of puzzle to be parsed.
        
        Returns:         List of lists, where a single value in such a nested list
                         corresponds to a single cell from the parsed grid. The None value
                         is used for undefined cells, int values between 1 and 9 are used
                         for defined cells.

        Raises:
            InvalidInputError   If the given input is invalid (e.g. crippled grid, invalid
                                cell values etc.).
        """
        with StringIO(grid_as_string.strip()) as input:
            parser = PuzzleParser(input)
            return parser.__get_cells()


    def __parse_border_line(self, index: int):
        if index >= len(self._lines):
            raise InvalidInputError("Row {0} is missing.".format(index + 1))
        if self._lines[index] != _border_line_template():
            raise InvalidInputError("Row {0} is not a valid border line.".format(index + 1))


    def __parse_cell_line(self, row_index: int) -> List[int]:
        template = _cell_line_template()
        result = []
        if row_index >= len(self._lines):
            raise InvalidInputError("Row {0} is missing.".format(row_index + 1))
        if (len(self._lines[row_index])) != len(template):
            raise InvalidInputError("Row {0} is not a valid cell line.".format(row_index + 1))
        for char_index in range(0, len(template)):
            if template[char_index] == '?':
                cell_value = self.__parse_and_validate_cell_value(row_index, char_index)
                result.append(cell_value)
            elif template[char_index] != self._lines[row_index][char_index]:
                raise InvalidInputError("Row {0} is not a valid cell line.".format(row_index + 1))
        return result


    def __parse_and_validate_cell_value(self, row_index: int, char_index: int) -> Optional[int]:
        if self._lines[row_index][char_index] not in " 123456789":
            raise InvalidInputError("Invalid cell value '{0}' found in row {1}.".format(self._lines[row_index][char_index], row_index + 1))
        if self._lines[row_index][char_index] == ' ':
            return None
        return int(self._lines[row_index][char_index])

    def __get_cells(self) -> List[List[int]]:
        result = []
        for index in range(0, 13):
            if index in [1, 2, 3, 5, 6, 7, 9, 10, 11]:
                cell_values = self.__parse_cell_line(index)
                result.append(cell_values)
            if index in [0, 4, 8, 12]:
                self.__parse_border_line(index)
        return result


class GridFormatter:
    """
    Simple formatter that can take an instance of the grid.Grid class and generate
    a textual grid presenting the cell values of the given grid. The textual
    representation can be written to a file, to the stdout, or to a string.

    Note:
        This class is not supposed to be directly instantiated by other classes.
        Instead, use the public static methods provided by this class. They are
        very easy to use, and they also take care about the proper release of
        resources like open files.
    """

    def __init__(self, grid, output, use_colors):
        """
        Internal initializer which is not to be used directly. Constructs a new formatter
        that will format the given grid.

        Args:
            grid:           The grid to be formatted.
            output:         Any text I/O object the generated texttual representation
                            is to be written to. It can be any class derived from
                            io.TextIOBase, e.g. io.StringIO.
            use_colors:     True if ANSI escape sequences are to be used to highlight
                            predefined cells (and thus distinguish them from the
                            completed cells); False otherwise.
        """
        self.grid = grid
        self.output = output
        self.use_colors = use_colors


    @staticmethod
    def write_to_file(grid: Grid, filename: str):
        """
        Writes the given grid to the file with the given filename.

        Args:
            grid:        The grid to be formatted.
            filename:    The name of the output file the generated textual
                         representation of the given grid is to be written
                         to.
        """
        with open(filename, "w") as file:
            formatter = GridFormatter(grid, output = file, use_colors = False)
            formatter.__write()


    @staticmethod
    def write_to_console(grid: Grid):
        """
        Writes the given grid to the standard output. In order to distinguish
        predefined cells from completed cells, ANSI escape sequences are used
        to tweak the font weight and colors.

        Args:
            grid:   The grid to be formatted.
        """
        formatter = GridFormatter(grid, output = stdout, use_colors = True)
        formatter.__write()


    @staticmethod
    def write_to_string(grid: Grid) -> str:
        """
        Writes the given grid to a string and returns the string.

        Args:
            grid:   The grid to be formatted.

        Returns:
            The created string representation of the given grid.
        """
        with StringIO() as output:
            formatter = GridFormatter(grid, output = output, use_colors = False)
            formatter.__write()
            return output.getvalue()


    def __write(self):
        self.__write_border()
        for row in range(0, 3):
            self.__write_cells(row)
        self.__write_border()
        for row in range(3, 6):
            self.__write_cells(row)
        self.__write_border()
        for row in range(6, 9):
            self.__write_cells(row)
        self.__write_border()


    def __write_border(self):
        self.output.write(_border_line_template())
        self.output.write("\n")


    def __write_cells(self, row: int):
        output = _cell_line_template()
        for column in range(0, 9):
            cell_value = " "
            if self.grid.get_cell_status(row, column) != CellStatus.UNDEFINED:
                cell_value = str(self.grid.get_cell_value(row, column))
            if self.use_colors and self.grid.get_cell_status(row, column) == CellStatus.PREDEFINED:
                cell_value = self.__decorate_with_color(cell_value)
            output = output.replace("?", cell_value, 1)
        self.output.write(output)
        self.output.write("\n")


    def __decorate_with_color(self, cell_value: str) -> str:
        return "\x1b[1;31;47m" + cell_value + "\x1b[0m"

