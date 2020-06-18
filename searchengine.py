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
This module provides the search engine and other data types participating on the
public API of the search engine.
"""

from enum import Enum, unique
from logging import getLogger
from time import perf_counter
from typing import List, Optional

from algorithmregistry import SearchAlgorithmRegistry
from grid import Grid
from searchalgorithm import SearchStepOutcome


_logger =  getLogger()


@unique
class SearchOutcome(Enum):
    """
    Defines possible outcomes of a search. The meaning of particular enum elements is
    the following:
    * SOLUTION_FOUND indicates that the search for a solution has been successful (i.e.
      complete and valid grid derived from the original puzzle has been found).
    * PUZZLE_DEAD_END indicates that the search for solution has failed (i.e. the used
      search algorithm has failed to find complete and valid grid derived from the original
      puzzle), and the failure seems to be caused by the puzzle rather than by the
      limitations of the used search algorithm (i.e. other search algorithm is unlikely to
      find a solution for the puzzle). Assignment dead end means that there is at least one
      undefined cell, but no candidate is applicable to the cell as all values are already
      present in the corresponding row, column, or region (i.e. all 9 values are already
      excluded for the undefined cell).
    * ALGORITHM_DEAD_END indicates that the search for solution has failed (i.e. the
      used search algorithm has failed to find complete and valid grid derived from
      the original puzzle, and the failure might be caused by limitations of the used
      search algorithm (i.e. other search algorithm might be able to find a solution.
      Algorithm dead end means that for each of the undefined cells, there are two
      or more applicable candidate values. In other words, chances are there is a
      solution for the puzzle, but the used search algorithm is unable to cope with
      ambiguity. 
    * TIMEOUT indicates that the search for solution has failed due to timeout. In other
      words, the timeout for the search has already expired, and the used search algorithm
      has not found complete and valid grid derived from the original puzzle yet.   
    """

    SOLUTION_FOUND = 1

    PUZZLE_DEAD_END = 2

    ALGORITHM_DEAD_END = 3

    TIMEOUT = 4


class SearchSummary:
    """
    Immutable structure carrying detailed information about the outcome of a search
    including the solution (or final grid in case the search has led to dead end).
    """

    def __init__(self, original_puzzle: Grid, algorithm: str,
                 outcome: SearchOutcome, final_grid: Grid,
                 duration_millis: int, cell_values_tried: int):
        self._original_puzzle = original_puzzle
        self._algorithm = algorithm
        self._outcome = outcome
        self._final_grid = final_grid
        self._duration_millis = duration_millis
        self._cell_values_tried = cell_values_tried


    @property
    def original_puzzle(self) -> Grid:
        """
        The original puzzle passed to the search.
        """
        return self._original_puzzle


    @property
    def algorithm(self) -> str:
        """
        The name of the search algorithm used to solve the puzzle.
        """
        return self._algorithm


    @property
    def outcome(self) -> SearchOutcome:
        """
        The outcome of the search indicating whether a solution has been found,
        or a dead end or timeout has been encountered.
        """
        return self._outcome


    @property
    def final_grid(self) -> Grid:
        """
        The final grid achieved at the end of the search. In case of successful search,
        the return value of this method is the solution. In case of failed search
        (regardless of whether dead end or timeout), the return value of this method
        provides the state of the grid at the end of the search.
        """
        return self._final_grid


    @property
    def duration_millis(self) -> int:
        """
        The duration of the search in milliseconds.
        """
        return self._duration_millis


    @property
    def cell_values_tried(self) -> int:
        """
        The number of cell values tried during the search. This value can be
        used to assess the efficiency of the search algorithm.
        """
        return self._cell_values_tried


class InvalidPuzzleError(Exception):
    """
    Exception raised to indicate that a puzzle passed to the search engine
    * either violates the game rules by having at least one duplicate in a row, in
      a column, or in a region
    * or does not contain any undefined cells.
    """
    pass


class _Stopwatch:
    """
    Simple stopwatch used to measure the duration of a search.
    
    Note:
        This class is not supposed to be directly instantiated by other classes. 
        Instead, the static start() method is to be used.
    """

    def __init__(self):
        self.start_time: float = perf_counter()


    @staticmethod
    def start():
        return _Stopwatch()


    def elapsed_time_millis(self) -> int:
        duration = perf_counter() - self.start_time
        return int(1000 * duration)


    def elapsed_time_seconds(self) -> float:
        return perf_counter() - self.start_time


class _SearchJob:
    """
    Internal helper class supporting the implementation of the search engine. Single instance of
    this class drives a single search by invoking the search algorithm and evaluating the search
    step outcome.
    """

    def __init__(self, puzzle: Grid, algorithm, timeout_sec: int):
        self._puzzle = puzzle
        self._algorithm = algorithm
        self._timeout_sec = timeout_sec
        self._last_step_outcome = None
        self._duration_millis = None
        self._cell_values_tried = 0


    def execute(self):
        stopwatch = _Stopwatch.start()

        try:
            self._algorithm.start(self._puzzle)
            step_outcome = self._algorithm.next_step()
            self.__update_search_state(step_outcome)
            _logger.info("Very first search step completed, outcome = %s", step_outcome)
            while step_outcome == SearchStepOutcome.CONTINUE:
                if self._timeout_sec < stopwatch.elapsed_time_seconds():
                    _logger.error("Search not completed yet, timeout already reached")
                    message = "Timeout {0} sec has already expired ({1} cell values have been tried)."
                    raise TimeoutError(message.format(self._timeout_sec, self._cell_values_tried))
                step_outcome = self._algorithm.next_step()
                self.__update_search_state(step_outcome)
                _logger.info("Another search step completed, outcome = %s", step_outcome)
        finally:
            self._duration_millis = stopwatch.elapsed_time_millis()


    def __update_search_state(self, step_outcome: SearchStepOutcome):
        self._last_step_outcome = step_outcome
        if step_outcome in [SearchStepOutcome.CONTINUE, SearchStepOutcome.SOLUTION_FOUND]:
            self._cell_values_tried += 1


    @property
    def last_step_outcome(self) -> Optional[SearchStepOutcome]:
        return self._last_step_outcome


    @property
    def final_grid(self) -> Grid:
        return self._algorithm.last_step_outcome


    @property
    def cell_values_tried(self) -> int:
        return self._cell_values_tried


    @property
    def duration_millis(self) -> Optional[int]:
        return self._duration_millis


class SearchEngine:
    """
    Facade encapsulating the entire searching machinery including particular search
    algorithms.

    Note:
    The entire public API provided by this class consists of static method(s), there
    are no instance methods. Therefore, it does not make any sense to instantiate this
    class.
    """

    @staticmethod
    def find_solution(puzzle_cells: List[List[int]], algorithm_name: str, timeout_sec: int):
        """
        Tries to find a solution for the given puzzle using the given search algorithm.

        Args:
            puzzle_cells:       The cells of the puzzle to be solved. List of lists is
                                expected, where a single cell is to be represented by a
                                single value within a nested list. The None value is
                                expected for undefined cells, int values between 1 and 9
                                are expected for predefined cells.
            algorithm_name:     The name of the search algorithm to be used to solve the
                                puzzle.
            timeout_sec:        The maximal allowed duration of the search, in seconds.

        Returns:

        Raises:
            TimeoutError        If the given timeout expires before the desired search
                                algorithm solves the puzzle or comes to a dead end.
        """
        _logger.info("Going to start %s search (timeout = %d sec)", algorithm_name, timeout_sec)
        puzzle = Grid(puzzle_cells)
        if not puzzle.is_valid():
            _logger.error("Puzzle not valid")
            raise InvalidPuzzleError("The given puzzle violates the game rules. At least one value is present two or more times in a single row, single column, or single region.")
        if puzzle.is_complete():
            _logger.error("Puzzle already complete")
            raise InvalidPuzzleError("The given puzzle does not contain empty cells - there is nothing to be solved.")

        search_algorithm = SearchAlgorithmRegistry.create_algorithm_instance(algorithm_name)
        search_job = _SearchJob(puzzle.copy(), search_algorithm, timeout_sec)
        search_outcome = None

        try:
            search_job.execute()
            search_outcome = SearchEngine.__convert_to_search_outcome(search_job.last_step_outcome)
            if search_outcome == SearchOutcome.SOLUTION_FOUND:
                assert search_job.final_grid.is_valid()
        except TimeoutError:
            search_outcome = SearchOutcome.TIMEOUT

        _logger.info("Search finished, outcome = %s", search_outcome)
        return SearchSummary(original_puzzle = puzzle, algorithm = algorithm_name, outcome = search_outcome, final_grid = search_job.final_grid, duration_millis = search_job.duration_millis, cell_values_tried = search_job.cell_values_tried)


    @staticmethod
    def __convert_to_search_outcome(step_outcome):
        if step_outcome is SearchStepOutcome.SOLUTION_FOUND:
            return SearchOutcome.SOLUTION_FOUND
        if step_outcome is SearchStepOutcome.ALGORITHM_DEAD_END:
            return SearchOutcome.ALGORITHM_DEAD_END
        if step_outcome is SearchStepOutcome.PUZZLE_DEAD_END:
            return SearchOutcome.PUZZLE_DEAD_END

        message = "Cannot convert {0} to {1}.".format(step_outcome, SearchOutcome.__name__)
        raise ValueError(message)
