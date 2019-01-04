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
This module provides types that participate on the contract between the search engine and
the particular search algorithm implementations.
"""

from enum import Enum, unique

@unique
class SearchStepOutcome(Enum):
    """
    Defines possible outcomes of a single search step (i.e. single invocation of the
    next_step() method of a search algorithm). The meaning of the particular enum elements
    is the following:
    * CONTINUE indicates that the search step that has just finished was **NOT** the last
      one (i.e. the entire search has **NOT** finished yet). Further search step(s) have
      to be executed in order to finish the search as the grid is still incomplete, and
      there are still applicable candidate values which have not been tried yet. 
    * SOLUTION_FOUND indicates that the search step that has just finished was the last one
      (i.e. the entire search has finished), and the search has successfully found solution
      for the original puzzle.
    * PUZZLE_DEAD_END indicates that the search step that has just finished was the last
      one (i.e. the entire search has finished), and the search has failed to find complete
      and valid grid derived from the original puzzle. The failure seems to be caused by the
      assignment rather than by the limitations of the search algorithm (i.e. other search
      algorithm is unlikely to find a solution for the original puzzle).
    * ALGORITHM_DEAD_END indicates that the search step that has just finished was the last
      one (i.e. the entire search has finished), and the search has failed to find complete
      and valid grid derived from the original puzzle. The failure might be caused by
      limitations of the search algorithm (i.e. other search algorithm might be able to find
      a solution for the original puzzle).
    """

    CONTINUE = 1

    SOLUTION_FOUND = 2

    PUZZLE_DEAD_END = 3

    ALGORITHM_DEAD_END = 4

