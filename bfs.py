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
This module provides two implementations of the Breadth First Search algorithm which is
a brute force algorithm based on queue.
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
from typing import Tuple

from searchsupport import CandidateQueryMode, SearchSupport
from grid import Grid
from searchalgorithm import SearchStepOutcome

_logger = getLogger()

class _StepInput:
    """
    Internal helper class supporting the implementation of the BFS algorithm. Single
    instance of this class represents a single entry in the queue used by the BFS
    algorithm.
    """

    def __init__(self, search_support: SearchSupport, row: int, column: int, value: int):
        self._search_support = search_support
        self._row = row
        self._column = column
        self._value = value


    @property
    def search_support(self) -> SearchSupport:
        return self._search_support


    @property
    def cell_address(self) -> Tuple[int, int]:
        return (self._row, self._column)


    @property
    def value(self) -> int:
        return self._value


class _BreadthFirstSearch:
    """
    Base class providing functionality common to both breadth-first search (BFS)
    implementations of search algorithm.
    """

    def __init__(self, candidate_query_mode: CandidateQueryMode):
        self._queue = deque()
        self._candidate_query_mode = candidate_query_mode


    def start(self, puzzle: Grid):
        _logger.info("Starting the search")
        self._last_step_outcome = puzzle
        self.__enqueue_steps(SearchSupport(puzzle.copy()))


    def next_step(self) -> SearchStepOutcome:
        _logger.info("Starting the next search step")
        return self.__process_next_step_from_queue()


    @property
    def last_step_outcome(self) -> Grid:
        return self._last_step_outcome


    def __enqueue_steps(self, search_support: SearchSupport):
        if search_support.has_empty_cells_without_applicable_candidates():
            _logger.info("Empty cells without applicable candidates found, nothing will be added to queue")
            return
        candidate_list = search_support.get_undefined_cell_candidates(self._candidate_query_mode)
        assert len(candidate_list) > 0
        row, column = candidate_list.cell_address
        for single_value in candidate_list.values:
            self._queue.append(_StepInput(search_support.copy(), row, column, single_value))


    def __process_next_step_from_queue(self) -> SearchStepOutcome:
        if len(self._queue) == 0:
            _logger.info("Empty queue, going to abort the search")
            return SearchStepOutcome.PUZZLE_DEAD_END
        
        step_input = self._queue.popleft()
        search_support = step_input.search_support
        row, column = step_input.cell_address
        value = step_input.value

        search_support.set_cell_value(row, column, value)
        self._last_step_outcome = search_support.grid
        if search_support.has_completed_grid():
            _logger.info("Search completed, solution found")
            return SearchStepOutcome.SOLUTION_FOUND

        self.__enqueue_steps(search_support.copy())
        return SearchStepOutcome.CONTINUE


class NaiveBreadthFirstSearch(_BreadthFirstSearch):
    """
    Naive implementation of the BFS search algorithm.
    """

    def __init__(self):
        super().__init__(CandidateQueryMode.FIRST_UNDEFINED_CELL)


class SmartBreadthFirstSearch(_BreadthFirstSearch):
    """
    Smart implementation of the BFS search algorithm.
    """

    def __init__(self):
        super().__init__(CandidateQueryMode.UNDEFINED_CELL_WITH_LEAST_CANDIDATES)
