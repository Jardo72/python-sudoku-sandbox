#
# Copyright 2018 Jaroslav Chmurny
#
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
This module provides classes supporting implementation of search algorithms. Search
algorithm implementations should use the SearchSupport class which is more or less
a facade encapsulating the functionality provided by this module. They should not
use the other classes (except of the CandidateQueryMode enum) directly.
"""

from collections import deque, OrderedDict
from enum import Enum, unique
from logging import getLogger
from typing import List, Sequence, Optional, Tuple

from grid import Grid, CellStatus

_logger = getLogger()

@unique
class _ExclusionOutcome(Enum):
    """
    Defines possible outcomes of an exclusion, for instance an exclusion of a candidate
    value for a single undefined cell. The meaning of particular enum elements is the
    following:
    * UNAMBIGUOUS_CANDIDATE_FOUND indicates that after the exclusion of a candidate, there
      is only single applicable candidate remaining. This outcome inidcates that an
      unambiguous candidate has been found by the exclusion.
    * UNAMBIGUOUS_CANDIDATE_NOT_FOUND indicates that the exclusion has not identified an
      unambiguous candidate. This value is to be used in several situations, for instance
      if two or more applicable candidates are still remaining after the exclusion, or if
      the exclusion of a candidate has not changed the set of candidates as the candidate
      was already excluded.
    This enum is internal, there is no need to use it directly in other modules.
    """

    UNAMBIGUOUS_CANDIDATE_FOUND = 1

    UNAMBIGUOUS_CANDIDATE_NOT_FOUND = 2


@unique
class CandidateQueryMode(Enum):
    """
    Defines options how value exclusion logic can provide candidates for an undefined cell.
    The meaning of particular enum elements is the following:
    * FIRST_UNDEFINED_CELL indicates that the candidates for the first undefined cell
      are to be returned, regardless of how many candidates are applicable to the first
      undefined cell.
    * UNDEFINED_CELL_WITH_LEAST_CANDIDATES indicates that the candidates for the
      undefined cell with least applicable candidates are to be returned.
    """

    FIRST_UNDEFINED_CELL = 1

    UNDEFINED_CELL_WITH_LEAST_CANDIDATES = 2


class _BaseCandidateInfo:
    """
    Internal base class providing functionality common to UnambiguousCandidate and CandidateList
    classes.
    """

    def __init__(self, row: int, column: int):
        self._row = row
        self._column = column


    @property
    def cell_address(self) -> Tuple[int, int]:
        """
        The coordinates of the cell the candidate information carried by this object
        is applicable to.

        Returns:
            Tuple representing the above mentioned coordinates. The first element of the
            tuple is the row, the second element is the column. Zero corresponds
            to the first row or column, eight corresponds to the last row or column.
        """
        return (self._row, self._column)


    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        return self._row == other._row and self._column == other._column


    def __repr__(self):
        return "[row; column] = [{0}; {1}]".format(self._row, self._column)


class UnambiguousCandidate(_BaseCandidateInfo):
    """
    Immutable structure carrying information about an unambiguous candidate for an
    undefined cell. Besides the only applicable candidate value, this structure also
    carries the address (i.e. the row and the column) of the concerned cell.
    """

    def __init__(self, row: int, column: int, value: int):
        super().__init__(row, column)
        self._value = value


    @property
    def value(self) -> int:
        """
        The only candidate value applicable to the cell with the coordinates carried by this
        object.

        Returns:
            All canidate values applicable to the concerned cell at the time this object has
            been created. An empty tuple is returned if no candiate value is applicable to the
            concerned cell.
        """
        return self._value


    def __eq__(self, other):
        return super().__eq__(other) and self._value == other._value


    def __repr__(self):
        type_name = type(self).__name__
        return "{0}({1}, value = {2})".format(type_name, super().__repr__(), self._value)


class CandidateList(_BaseCandidateInfo):
    """
    Simple structure carrying all candidate values applicable to a single undefined
    cell. Besides the applicable candidate values, this structure also carries the
    address (i.e. the row and the column) of the concerned cell.
    """

    def __init__(self, row: int, column: int, values: Sequence[int]):
        super().__init__(row, column)
        self._values = tuple(values)


    @property
    def values(self) -> Tuple[int, ...]:
        """
        Returns a tuple with all candidate values applicable to the cell with the coordinates
        carried by this candidate list. 

        Returns:
            All canidate values applicable to the concerned cell at the time this object has
            been created. An empty tuple is returned if no candiate value is applicable to the
            concerned cell.
        """
        return self._values


    def __len__(self):
        return len(self._values)


    def __eq__(self, other):
        return super().__eq__(other) and sorted(self._values) == sorted(other._values)


    def __repr__(self):
        type_name = type(self).__name__
        return "{0}({1}, values = {2})".format(type_name, super().__repr__(), self._values)


class _CellPeers:
    """
    Internal helper class that creates a list of peers for every single cell contained in a Sudoku
    grid. For a cell, the peers are other cells contained in the same row, in the same column, or
    in the same region. Peers play a vital role in the exclusion logic provided by this module.
    """

    @staticmethod
    def create():
        result = []
        for row in range(0, 9):
            cells_in_row = [tuple(_CellPeers.__create_for_single_cell(row, column)) for column in range(0, 9)]
            result.append(tuple(cells_in_row))
        return tuple(result)


    @staticmethod
    def __create_for_single_cell(row: int, column: int):
        peers_in_row = [(row, c) for c in range(0, 9) if c != column]
        peers_in_column = [(r, column) for r in range(0, 9) if r != row]

        topmost_row = 3 * (row // 3)
        leftmost_column = 3 * (column // 3)
        peers_in_region = [(r, c) for r in range(topmost_row, topmost_row + 3) for c in range(leftmost_column, leftmost_column + 3)]
        peers_in_region.remove((row, column))

        return OrderedDict((address, True) for address in (peers_in_row + peers_in_column + peers_in_region)).keys()


class _CandidateValues:
    """
    Internal helper that keeps track of applicable candidate values for a single cell. An
    instance of this class is to be updated whenever one of the peers of the cell corresponding
    to the instance of this class is updated. For better understanding, let's assume the
    following example. An instance of this class corresponds to an undefined cell. The row
    containing the cell contains another undefined cells, and the value of one of them is set
    to 5. The above mentioned instance of this class has to be updated via the exclude_value
    method as the value 5 is not applicable anymore.
    """

    def __init__(self, bitmask: int = 0b111111111, applicable_value_count: int = 9):
        self._bitmask = bitmask
        self._applicable_value_count = applicable_value_count


    def clear(self):
        self._bitmask = 0
        self._applicable_value_count = 0


    def get_applicable_value_count(self) -> int:
        return self._applicable_value_count


    def exclude_value(self, value: int):
        _logger.debug("Going to exclude the value %d, bitmask before exclusion = %s", value, format(self._bitmask, "b"))
        value_mask = 1 << (value - 1)
        if self._bitmask & value_mask == value_mask:
            self._bitmask ^= value_mask
            _logger.debug("Bitmask after exclusion = %s", format(self._bitmask, "b"))
            self._applicable_value_count -= 1
            if self._applicable_value_count == 1:
                return _ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_FOUND
        return _ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND


    def get_applicable_values(self) -> Tuple[int, ...]:
        result = [value for value in range(1, 10) if self._bitmask & (1 << (value - 1))]
        return tuple(result)


    def get_single_remaining_applicable_value(self) -> int:
        if self._applicable_value_count != 1:
            message = "Cannot provide single remaining applicable value ({0} candidates remaining)."
            raise RuntimeError(message.format(self._applicable_value_count))
        for value in range(1, 10):
            if self._bitmask == (1 << (value - 1)):
                return value


    def is_applicable(self, value: int) -> bool:
        value_mask = 1 << (value - 1)
        return self._bitmask & value_mask == value_mask


    def copy(self):
        """
        Creates and returns a deep copy of this object.
        """
        return _CandidateValues(self._bitmask, self._applicable_value_count)


class _CandidateValueExclusionLogic:
    """
    Logic responsible for exclusion of candidate values inapplicable to particular cells.
    For instance, if the value of a cell is set to 5, the value 5 is excluded for all
    cells within the same row, column, and region. If a single candidate value remains
    applicable to a cell, that value is considered as unambiguous candidate for that
    cell. This class is an internal helper which should not be used directly by other
    modules.
    """

    __cell_peers = _CellPeers.create()


    def __init__(self, original_exclusion_logic = None):
        if original_exclusion_logic is None:
            self._candidates =  _CandidateValueExclusionLogic.__create_candidates_from_scratch()
        else:
            self._candidates = _CandidateValueExclusionLogic.__create_candidates_from_other_instance(original_exclusion_logic)


    @staticmethod
    def __create_candidates_from_scratch():
        rows = []
        for _ in range(0, 9):
            rows.append(tuple([_CandidateValues() for column in range(0, 9)]))
        return tuple(rows)


    @staticmethod
    def __create_candidates_from_other_instance(original_exclusion_logic):
        rows = []
        for row in range(0, 9):
            rows.append(tuple([original_exclusion_logic._candidates[row][column].copy() for column in range(0, 9)]))
        return tuple(rows)


    @staticmethod
    def create_from(grid: Grid):
        """
        Creates and returns a new CandidateValueExclusionLogic instance. Before returning
        the above mentioned instance, candidate value exclusion is performed reflecting the
        predefined and completed cells of the given grid.

        Args:
            grid:

        Returns:
            The created CandidateValueExclusionLogic instance.
        """
        exclusion_logic = _CandidateValueExclusionLogic()
        for (row, column) in Grid.get_all_cell_addresses():
            if grid.get_cell_status(row, column) is not CellStatus.UNDEFINED:
                value = grid.get_cell_value(row, column)
                exclusion_logic.apply_and_exclude_cell_value(row, column, value)
        return exclusion_logic


    def apply_and_exclude_cell_value(self, row: int, column: int, value: int):
        """
        Applies the given cell value to the cell with the given coordinates and excludes
        the given cell value for the peers of the cell with the coordinates.

        Args:
            row (int):      The row coordinate of the cell the given value is to
                            be applied to. Zero corresponds to the first row, eight
                            corresponds to the last row.
            column (int)    The column coordinate of the cell the given value is to
                            be applied to. Zero corresponds to the first column, eight
                            corresponds to the last column.
            value (int):    The value for the given cell.

        Returns:
            List of UnambiguousCandidate instances, one for each of those peers of the concerned
            cell for which just a single applicable candidate value has remained after the
            exclusion. None is returned if there is no such peer.
        """
        _logger.debug("Going to apply candidate value %d to cell [%d, %d]", value, row, column)
        self._candidates[row][column].clear()
        result = None
        for cell in _CandidateValueExclusionLogic.__cell_peers[row][column]:
            row, column = cell
            _logger.debug("Going to exclude candidate value %d for cell [%d, %d]", value, row, column)
            exclusion_outcome = self._candidates[row][column].exclude_value(value)
            _logger.debug("Exclusion outcome = %s", exclusion_outcome)
            if exclusion_outcome is _ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_FOUND:
                result = result if result is not None else []
                candidate_list = UnambiguousCandidate(row, column, self._candidates[row][column].get_single_remaining_applicable_value())
                result.append(candidate_list)
        return result


    def get_undefined_cell_candidates(self, mode: CandidateQueryMode):
        """
        Returns a list of candidate values applicable to one of the undefined cells.

        Args:
            mode:    Determines which the undefined cell for which the candidate values
                     are to be provided.

        Returns:
            New CandidateList instance carrying the applicable candidate values as well
            as the address of the undefined cell the candidate values are applicable to.

        Raises:
            ValueError:   If unexpected mode is received.
        """
        if mode is CandidateQueryMode.FIRST_UNDEFINED_CELL:
            return self.__get_candidates_for_first_undefined_cell()
        elif mode is CandidateQueryMode.UNDEFINED_CELL_WITH_LEAST_CANDIDATES:
            return self.__get_candidates_for_undefined_cell_with_least_candidates()

        message = "Unexpected candidate query mode {0}".format(mode)
        raise ValueError(message)


    def __get_candidates_for_first_undefined_cell(self) -> Optional[CandidateList]:
        for (row, column) in Grid.get_all_cell_addresses():
            if self._candidates[row][column].get_applicable_value_count() > 0:
                values = self._candidates[row][column].get_applicable_values()
                return CandidateList(row, column, values)
        return None


    def __get_candidates_for_undefined_cell_with_least_candidates(self):
        candidate_list = None
        for (row, column) in Grid.get_all_cell_addresses():
            count_for_current_cell = self._candidates[row][column].get_applicable_value_count()
            if count_for_current_cell == 0:
                continue
            if candidate_list is None or count_for_current_cell < len(candidate_list):
                candidate_list = CandidateList(row, column, self._candidates[row][column].get_applicable_values())
        return candidate_list


    def is_applicable(self, unambiguous_candidate) -> bool:
        """
        Verifies whether the given unambiguous candidate is applicable.

        Args:
            unambiguous_candidate: The unambiguous candidate to be verified.

        Returns:
            True if and only of the candidate value carried by the given candidate
            object is applicable to the cell with the coordinates carried by the
            given candidate object. False if the concerned cell is not empty, or if
            the concerned cell value is already present in the row, column, or region
            containing the concerned cell.
        """
        row, column = unambiguous_candidate.cell_address
        value = unambiguous_candidate.value
        return self._candidates[row][column].is_applicable(value)


    def get_applicable_value_count(self, row: int, column: int) -> int:
        """
        Returns the number of candidate values applicable to the cell with the given
        coordinates.

        Args:
            row (int):      The row coordinate of the cell for which the number of
                            applicable candidate values is to be returned. Zero
                            corresponds to the first row, eight corresponds to the
                            last row.
            column (int):   The column coordinate of the cell for which the number of
                            candidate values is to be returned. Zero corresponds to
                            the first column, eight corresponds to the last column.
        """
        return self._candidates[row][column].get_applicable_value_count()


    def copy(self):
        """
        Creates and returns a deep copy of this object.
        """
        return _CandidateValueExclusionLogic(self)


class _RegionCandidateCells:
    """
    Keeps track of cells within a region where a particular value is applicable.
    """

    __row_peers = {0: 0b111111000, 1: 0b111000111, 2: 0b000111111}

    __column_peers = {0: 0b110110110, 1: 0b101101101, 2: 0b011011011}

    def __init__(self, topmost_row, leftmost_column, value, bitmask = 0b111111111, applicable_cell_count = 9):
        self._topmost_row = topmost_row
        self._leftmost_column = leftmost_column
        self._value = value
        self._bitmask = bitmask
        self._applicable_cell_count = applicable_cell_count


    def apply_and_exclude_cell_value(self, row: int, column: int, value: int):
        _logger.debug("Going to apply/exclude value %d for [%d, %d]", value, row, column)
        row_within_region, column_within_region = self.__get_cell_coordinates_within_this_region(row, column)
        _logger.debug("Cell address within region [%d, %d]", row_within_region, column_within_region)
        if (row_within_region, column_within_region) == (-1, -1):
            # cell not contained in this region, and neither the row, nor the column
            # containing the cell is crossing this region => nothing to be excluded
            _logger.debug("Ignoring region starting at [%d, %d] for the value %d", self._topmost_row, self._leftmost_column, self._value)
            return _ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND

        if row_within_region in [0, 1, 2] and column_within_region not in [0, 1, 2]:
            _logger.debug("Row is crossing this region")
            # cell not contained in this region, but the row containing the cell is
            # crossing this region; depending on the value, we have to exclude either
            # nothing, or all peers of the cell
            if value != self._value:
                _logger.debug("Ignoring the value %d (my value is %d)", value, self._value)
                return _ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND
            peers_mask = _RegionCandidateCells.__row_peers[row_within_region]
            _logger.debug("Peers mask (row) = %s, current status = %s", format(peers_mask, 'b'), format(self._bitmask, 'b'))
            self._bitmask = self._bitmask & peers_mask
            _logger.debug("New status = %s", format(self._bitmask, 'b'))
            return self.__update_applicable_value_count()

        if column_within_region in [0, 1, 2] and row_within_region not in [0, 1, 2]:
            _logger.debug("Column is crossing this region")
            # cell not contained in this region, but the column containing the cell is
            # crossing this region; depending on the value, we have to exclude either
            # nothing, or all peers of the cell
            if value != self._value:
                _logger.debug("Ignoring the value %d (my value is %d)", value, self._value)
                return _ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND
            peers_mask = _RegionCandidateCells.__column_peers[column_within_region]
            _logger.debug("Peers mask (column) = %s, current status = %s", format(peers_mask, 'b'), format(self._bitmask, 'b'))
            self._bitmask = self._bitmask & peers_mask
            _logger.debug("New status = %s", format(self._bitmask, 'b'))
            return self.__update_applicable_value_count()

        # cell contained in this region; depending on the value, we have to exclude eihter
        # a single cell, or the entire region
        if self._value == value:
            _logger.debug("Excluding complete region")
            self._bitmask = 0
            self._applicable_cell_count = 0
            return _ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND

        _logger.debug("Excluding single cell")
        cell_mask = 1 << (3 * row_within_region + column_within_region)
        cell_mask = 0b111111111 ^ cell_mask
        self._bitmask = self._bitmask & cell_mask
        _logger.debug("New status = %s", format(self._bitmask, 'b'))
        return self.__update_applicable_value_count()


    def __get_cell_coordinates_within_this_region(self, row: int, column: int):
        row_within_region, column_within_region = (-1, -1)
        if (3 * (row // 3)) == self._topmost_row:
            row_within_region = row - self._topmost_row
        if (3 * (column // 3)) == self._leftmost_column:
            column_within_region = column - self._leftmost_column

        return (row_within_region, column_within_region)


    def __update_applicable_value_count(self) -> _ExclusionOutcome:
        new_count = 0
        for shift in range(0, 9):
            mask = 1 << shift
            if self._bitmask & mask == mask:
                new_count += 1
        
        _logger.debug("Going to update the value count from %d to %d", self._applicable_cell_count, new_count)
        result = _ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND
        if new_count == 1 and self._applicable_cell_count > new_count:
            result = _ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_FOUND
        self._applicable_cell_count = new_count
        return result


    def get_single_remaining_applicable_cell(self):
        if self._applicable_cell_count != 1:
            message = "Cannot provide single remaining applicable cell ({0} candidates remaining)."
            raise RuntimeError(message.format(self._applicable_value_count))
        _logger.debug("Remaining bitmask = %s", format(self._bitmask, 'b'))
        for i in range(0, 9):
            mask = 1 << i
            if self._bitmask & mask == mask:
                row = self._topmost_row + (i // 3)
                column = self._leftmost_column + (i % 3)
                result = UnambiguousCandidate(row, column, self._value)
                _logger.debug("%s will be returned", result)
                return result
        _logger.debug("None will be returned")


    def copy(self):
        """
        Creates and returns a deep copy of this object.
        """
        return _RegionCandidateCells(self._topmost_row, self._leftmost_column, self._value, self._bitmask, self._applicable_cell_count)


class _RegionGrid:
    """
    Helper class supporting candidate cell exclusion. Single instance of this class
    aggregates 9 instances of _RegionCandidateCells.
    """

    def __init__(self, value: Optional[int], regions: Sequence[_RegionCandidateCells] = None):
        if regions is None:
            self._regions = tuple([_RegionCandidateCells(row, column, value) for row in [0, 3, 6] for column in [0, 3, 6]])
        else:
            self._regions = tuple(regions)


    def apply_and_exclude_cell_value(self, row: int, column: int, value: int):
        result = None
        for region in self._regions:
            exclusion_outcome = region.apply_and_exclude_cell_value(row, column, value)
            if exclusion_outcome is _ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_FOUND:
                result = result if result is not None else []
                candidate = region.get_single_remaining_applicable_cell()
                result.append(candidate)
        return result


    def copy(self):
        """
        Creates and returns a deep copy of this object.
        """
        regions_copy = tuple([single_region.copy() for single_region in self._regions])
        return _RegionGrid(None, regions_copy)


class _CandidateCellExclusionLogic:
    """
    Logic responsible for exclusion of candidate cells where a particular value is
    not applicable. The exclusion leads to identification of the only cell within
    a region where a value is applicable. For such a cell, the value is considered
    as unambiguous candidate value. This class is an internal helper that should
    not be used directly by other modules.
    """

    def __init__(self, original_exclusion_logic = None):
        if original_exclusion_logic is None:
            self._region_grids = tuple([_RegionGrid(value) for value in range(1, 10)])
        else:
            self._region_grids = tuple([grid.copy() for grid in original_exclusion_logic._region_grids])


    def apply_and_exclude_cell_value(self, row: int, column: int, value: int):
        """
        Applies the given cell value to the cell with the given coordinates and excludes
        all peers of the given cell as candidate cells for the given value.

        Args:
            row (int):      The row coordinate of the cell the given value is to
                            be applied to. Zero corresponds to the first row, eight
                            corresponds to the last row.
            column (int)    The column coordinate of the cell the given value is to
                            be applied to. Zero corresponds to the first column, eight
                            corresponds to the last column.
            value (int):    The value for the given cell.

        Returns:
            List of UnambiguousCandidate instances, one for each of those cells which have
            been identified as unambiguous candidate cells with any region for any value.
            None is returned if the exclusion has not led to any cell being identified as
            unambiguous candidate cell.
        """
        _logger.debug("Going to apply & exclude the value %d for the cell [%d, %d]", value, row, column)
        result = None
        for grid in self._region_grids:
            partial_result = grid.apply_and_exclude_cell_value(row, column, value)
            if partial_result is not None:
                result = result if result is not None else []
                result += partial_result
        return result

    
    def copy(self):
        """
        Creates and returns a deep copy of this object.
        """
        return _CandidateCellExclusionLogic(self)


class _ExclusionLogic:
    """
    Composite that aggregates and coordinates _CandidateValueExclusionLogic and
    _CandidateCellExclusionLogic. This class is an internal helper that should not
    be used directly by other modules.
    """

    def __init__(self, candidate_value_exclusion = None, candidate_cell_exclusion = None):
        if candidate_value_exclusion is None:
            candidate_value_exclusion = _CandidateValueExclusionLogic()
        self._candidate_value_exclusion = candidate_value_exclusion
        if candidate_cell_exclusion is None:
            candidate_cell_exclusion = _CandidateCellExclusionLogic()
        self._candidate_cell_exclusion = candidate_cell_exclusion


    def apply_and_exclude_cell_value(self, row: int, column: int, value: int):
        """
        Applies the given cell value to the cell with the given coordinates and excludes
        the given cell value for the peers of the cell with the coordinates.

        Args:
            row (int):      The row coordinate of the cell the given value is to
                            be applied to. Zero corresponds to the first row, eight
                            corresponds to the last row.
            column (int)    The column coordinate of the cell the given value is to
                            be applied to. Zero corresponds to the first column, eight
                            corresponds to the last column.
            value (int):    The value for the given cell.

        Returns:
            List of UnambiguousCandidate instances, one for each of those cells for which just
            a single applicable candidate value has remained after the exclusion. None is returned
            if there is no such peer.
        """
        _logger.debug("Going to apply & exclude the value %d for the cell [%d, %d]", value, row, column)
        result = None
        list = self._candidate_value_exclusion.apply_and_exclude_cell_value(row, column, value)
        if list is not None:
            _logger.debug("There are %d candidates from candidate value exclusion", len(list))
            result = []
            result.extend(list)
        list = self._candidate_cell_exclusion.apply_and_exclude_cell_value(row, column, value)
        if list is not None:
            _logger.debug("There are %d candidates from candidate cell exclusion", len(list))
            result = [] if result is None else result
            result.extend(list)
        return result


    def is_applicable(self, unambiguous_candidate) -> bool:
        """
        Verifies whether the given unambiguous candidate is applicable.

        Args:
            unambiguous_candidate: The unambiguous candidate to be verified.

        Returns:
            True if and only of the candidate value carried by the given candidate
            object is applicable to the cell with the coordinates carried by the
            given candidate object. False if the concerned cell is not empty, or if
            the concerned cell value is already present in the row, column, or region
            containing the concerned cell.
        """
        return self._candidate_value_exclusion.is_applicable(unambiguous_candidate)


    def get_applicable_value_count(self, row: int, column: int) -> int:
        """
        Returns the number of candidate values applicable to the cell with the given
        coordinates.

        Args:
            row (int):      The row coordinate of the cell for which the number of
                            applicable candidate values is to be returned. Zero
                            corresponds to the first row, eight corresponds to the
                            last row.
            column (int):   The column coordinate of the cell for which the number of
                            candidate values is to be returned. Zero corresponds to
                            the first column, eight corresponds to the last column.
        """
        return self._candidate_value_exclusion.get_applicable_value_count(row, column)


    def get_undefined_cell_candidates(self, mode: CandidateQueryMode):
        """
        Returns a list of candidate values applicable to one of the undefined cells.

        Args:
            mode:    Determines which the undefined cell for which the candidate values
                     are to be provided.

        Returns:
            New CandidateList instance carrying the applicable candidate values as well
            as the address of the undefined cell the candidate values are applicable to.
            None is returned if there is no undefined cell, or no candidate is applicable
            to any of the undefined cells.
        """
        return self._candidate_value_exclusion.get_undefined_cell_candidates(mode)


    def copy(self):
        """
        Creates and returns a deep copy of this object.
        """
        return _ExclusionLogic(self._candidate_value_exclusion.copy(), self._candidate_cell_exclusion.copy())


class SearchSupport:
    """
    Facade encapsulating the functionality provided by this module. An instance of
    this class coordinates a grid with exclusion logic keeping track of applicable
    candidate values for the grid.
    """

    def __init__(self, grid: Grid = None, original = None):
        """
        Initializer allowing to create a new instance of this class either based on
        the given Grid, or as a clone of the given SearchSupport instance. In any of
        the two cases, use only one of the two arguments - the other must be None.

        Args:
            grid:           The grid the new search support is to be based on. If you
                            want to create a copy of an existing search support, use
                            None.
            original:       Original search support that is to be cloned. Use None if
                            you want to create a new search support based on a grid.
        """
        if SearchSupport.__is_ordinary_constructor(grid, original):
            self.__init_from_scratch(grid)
        elif SearchSupport.__is_copy_constructor(grid, original):
            self.__init_from_other_instance(original)
        else:
            message = "Invalid arguments. Exactly one of the two arguments is expected."
            raise ValueError(message)


    @staticmethod
    def __is_ordinary_constructor(grid: Grid, original) -> bool:
        return original is None and isinstance(grid, Grid)


    def __init_from_scratch(self, grid):
        self._exclusion_logic = _ExclusionLogic()
        self._candidate_queue = deque()
        self._grid = grid
        for (row, column) in Grid.get_all_cell_addresses():
            if grid.get_cell_status(row, column) is CellStatus.PREDEFINED:
                value = grid.get_cell_value(row, column)
                candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row, column, value)
                if candidate_list is not None:
                    self._candidate_queue.extend(candidate_list)


    @staticmethod
    def __is_copy_constructor(grid: Grid, original) -> bool:
        return grid is None and isinstance(original, SearchSupport)


    def __init_from_other_instance(self, original):
        self._exclusion_logic = original._exclusion_logic.copy()
        self._candidate_queue = deque()
        self._grid = original._grid.copy()


    @property
    def grid(self) -> Grid:
        """
        Provides a clone of the underlying grid.
        """
        return self._grid.copy()


    def has_completed_grid(self) -> bool:
        """
        Verifies whether the underlying grid is already completed.

        Returns:
            True if and only if none of the cells of the underlying grid is empty; False if
            the underlying grid contains at least one empty value.
        """
        return self._grid.is_complete()


    def set_cell_value(self, row: int, column: int, value: int):
        """
        Sets the cell with the given coordinates to the given value, assumed the
        cell with the given coordinates is empty (i.e. its value is undefined).
        Subsequently, excludes the given value from applicable candidate values
        for the peers of the given cell. If the exclusion identifies unambiguous
        candidate(s) for any undefined cell(s), the unambiguous candidates are
        retained so that they can be provided by the get_unambiguous_candidate
        method.

        Args:
            row (int):      The row coordinate of the cell whose value is to
                            be set. Zero corresponds to the first row, eight
                            corresponds to the last row.
            column (int):   The column coordinate of the cell whose value is to
                            be set. Zero corresponds to the first column, eight
                            corresponds to the last column.
            value (int):    The new value for the given cell.

        Raises:
            ValueError      If the given cell has already a value, regardless
                            of whether the value was defined in the original
                            puzzle or completed during the search.
        """
        self._grid.set_cell_value(row, column, value)
        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row, column, value)
        _logger.info("Assignment [%d, %d] = %d completed, outcome of exclusion is %s", row, column, value, candidate_list)
        if candidate_list is not None:
            self._candidate_queue.extend(candidate_list)


    def has_empty_cells_without_applicable_candidates(self) -> bool:
        """
        Verifies whether the underlying grid contains at least one undefined cell for
        which all nine values have been already excluded (i.e. no candidate value is
        applicable to the cell).

        Returns:
            True if and only if the underlying grid contains at least one undefined cell
            for which all nine values have been already excluded. False if at least one
            candidate value is applicable to each undefined cell of underlying grid.
        """
        for (row, column) in Grid.get_all_cell_addresses():
            cell_status = self._grid.get_cell_status(row, column)
            if cell_status is not CellStatus.UNDEFINED:
                continue
            if self._exclusion_logic.get_applicable_value_count(row, column) == 0:
                _logger.info("Cell [%d, %d] undefined, but there are no applicable candidates", row, column)
                return True
        return False


    def get_unambiguous_candidate(self):
        """
        Returns the next unambiguous candidate identified by one of the former
        invocations of the set_cell_value method. None is returned if there is
        no such unambiguous candidate.
        """
        while len(self._candidate_queue) > 0:
            candidate = self._candidate_queue.popleft()
            _logger.debug("Candidate taken from queue: %s", candidate)
            if self._exclusion_logic.is_applicable(candidate):
                _logger.debug("Candidate still applicable, going to return it")
                return candidate
            else:
                _logger.debug("Candidate not applicable anymore, cannot return it")
        return None


    def get_undefined_cell_candidates(self, mode: CandidateQueryMode):
        """
        Returns candidate values applicable to one of the undefined cells of the
        underlying grid.

        Args:
            mode:    One of the elements of the CandidateQueryMode enum determining
                     which of the undefined cells of the underlying grid is to be
                     taken into account.
        """
        result = self._exclusion_logic.get_undefined_cell_candidates(mode)
        if result:
            _logger.info("Undefined cell candidates found (mode = %s): %s", mode, result)
            row, column = result.cell_address
            assert self._grid.get_cell_status(row, column) is CellStatus.UNDEFINED
        else:
            _logger.debug("No undefined cell candidates, returning None")
        return result


    def copy(self):
        """
        Creates and returns a deep copy of this object.
        """
        return SearchSupport(original = self)