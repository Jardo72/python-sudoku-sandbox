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
This module provides the Unambiguous Candidate Search (UCS) algorithm.
"""

from logging import getLogger

from grid import Grid
from searchalgorithm import AbstractSearchAlgorithm
from searchsupport import SearchSupport
from searchalgorithm import SearchStepOutcome

_logger = getLogger()

class UnambiguousCandidateSearch(AbstractSearchAlgorithm):
    """
    Implementation of the UCS search algorithm.
    """

    def start(self, puzzle: Grid):
        _logger.info("Starting the search")
        self._search_support = SearchSupport(grid = puzzle)


    def next_step(self) -> SearchStepOutcome:
        _logger.info("Starting the next search step")
        candidate = self._search_support.get_unambiguous_candidate()
        if candidate is None:
            _logger.info("No applicable candidate found in queue, going to abort the search")
            if self._search_support.has_empty_cells_without_applicable_candidates():
                return SearchStepOutcome.PUZZLE_DEAD_END
            else:
                return SearchStepOutcome.ALGORITHM_DEAD_END

        row, column = candidate.cell_address
        value = candidate.value

        self._search_support.set_cell_value(row, column, value)

        if self._search_support.has_completed_grid():
            _logger.info("Search completed, solution found")
            return SearchStepOutcome.SOLUTION_FOUND

        return SearchStepOutcome.CONTINUE


    @property
    def last_step_outcome(self) -> Grid:
        return self._search_support.grid
