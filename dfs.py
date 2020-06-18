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
This module provides two implementations of the Depth First Search algorithm which is
a brute force algorithm based on stack.
* The smart implementation is searching for undefined cells with least applicable
  candidates, thus maximizing the likelihood that a tried candidate will be the
  right one.
* The naive one is simply searching for the first undefined cell (starting in the upper
  left corner of the grid) and trying its applicable candidates. The likelihood that
  the search will go to a wrong direction is pretty high, and this implementation
  typically tries significantly more candidates compared to the above mentioned smart
  implementation. The naive search is correspondingly slow compared to the smart one.
"""

from collections import deque
from logging import getLogger

from grid import Grid
from searchsupport import CandidateQueryMode, SearchSupport
from searchalgorithm import SearchStepOutcome

_logger = getLogger()

class _SearchGraphNode:
    """
    Internal helper class supporting the implementation of the DFS algorithm. Single
    instance of this class represents a single entry in the stack used by the DFS
    algorithm.
    """

    def __init__(self, search_support, candidate_list):
        self._search_support = search_support
        self._candidate_list = candidate_list
        self._current_index = 0
        assert len(candidate_list) > 0


    @property
    def search_support(self):
        return self._search_support


    @property
    def cell_address(self):
        return self._candidate_list.cell_address


    @property
    def already_exhausted(self) -> bool:
        if self._candidate_list is None:
            return True
        return self._current_index >= len(self._candidate_list)


    def next_value(self):
        values = self._candidate_list.values
        result = values[self._current_index]
        self._current_index += 1
        return result


    def __repr__(self):
        template = "{0}(cell = [{1}, {2}], value(s) = [{3}], next value = {4})"
        type_name = type(self).__name__
        row, column = self.cell_address
        values = ", ".join(map(str, self._candidate_list.values))
        return template.format(type_name, row, column, values, self.__current_value)


    @property
    def __current_value(self):
        if self._current_index >= len(self._candidate_list):
            return None
        return self._candidate_list.values[self._current_index]


class _SearchGraphNodeStack:
    """
    Internal helper class supporting the implementation of the DFS algorithm. This class
    implements the stack used by the DFS algorithm.
    """

    def __init__(self):
        self._entries = deque()


    def push(self, node):
        self._entries.append(node)
        _logger.debug("Node pushed to stack: %s", node)


    def backtrack_to_first_unexhausted_node(self):
        node = self.__peek()
        while node is not None and node.already_exhausted:
            self.__pop()
            node = self.__peek()
        _logger.debug("Backtracked to node %s", node)
        return node


    def __pop(self):
        if len(self._entries) == 0:
            return None
        return self._entries.pop()


    def __peek(self):
        if len(self._entries) == 0:
            return None
        return self._entries[-1]


class _DepthFirstSearch:
    """
    Base class providing functionality common to both depth-first search (DFS)
    implementations of search algorithm.
    """

    def __init__(self, candidate_query_mode: CandidateQueryMode):
        self._stack = _SearchGraphNodeStack()
        self._candidate_query_mode = candidate_query_mode


    def start(self, puzzle: Grid):
        _logger.info("Starting the search")
        self._last_step_outcome = puzzle
        search_support = SearchSupport(puzzle.copy())
        if search_support.has_empty_cells_without_applicable_candidates():
            _logger.info("Empty cells without applicable candidates found, nothing will be pushed to stack")
            return
        candidate_list = search_support.get_undefined_cell_candidates(self._candidate_query_mode)
        node = _SearchGraphNode(search_support, candidate_list)
        self._stack.push(node)


    def next_step(self) -> SearchStepOutcome:
        _logger.info("Starting the next search step")
        node = self._stack.backtrack_to_first_unexhausted_node()
        if node is None:
            _logger.info("Unexhausted node not found in the stack, going to abort the search")
            return SearchStepOutcome.PUZZLE_DEAD_END

        search_support = node.search_support
        row, column = node.cell_address
        value = node.next_value()

        search_support = search_support.copy()
        search_support.set_cell_value(row, column, value)
        self._last_step_outcome = search_support.grid
        if search_support.has_completed_grid():
            _logger.info("Search completed, solution found")
            return SearchStepOutcome.SOLUTION_FOUND

        if not search_support.has_empty_cells_without_applicable_candidates():
            candidate_list = search_support.get_undefined_cell_candidates(self._candidate_query_mode)
            node = _SearchGraphNode(search_support, candidate_list)
            self._stack.push(node)

        return SearchStepOutcome.CONTINUE


    @property
    def last_step_outcome(self) -> Grid:
        return self._last_step_outcome


class NaiveDepthFirstSearch(_DepthFirstSearch):
    """
    Naive implementation of the DFS search algorithm.
    """

    def __init__(self):
        super().__init__(CandidateQueryMode.FIRST_UNDEFINED_CELL)


class SmartDepthFirstSearch(_DepthFirstSearch):
    """
    Smart implementation of the DFS search algorithm.
    """

    def __init__(self):
        super().__init__(CandidateQueryMode.UNDEFINED_CELL_WITH_LEAST_CANDIDATES)
