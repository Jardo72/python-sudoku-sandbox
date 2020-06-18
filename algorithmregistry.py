# Copyright 2018 Jaroslav Chmurny
#
# This file is part of Python Sudoku Sandbox.
#
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
This module provides registry aware of all available search algorithms. The provided
registry class serves also as a factory able to instantiate the search algorithms. If
a new search algorithm has been implemented, it has to be added to this module.
"""

from logging import getLogger
from typing import Tuple

from bfs import NaiveBreadthFirstSearch, SmartBreadthFirstSearch
from dfs import NaiveDepthFirstSearch, SmartDepthFirstSearch
from ucs import UnambiguousCandidateSearch


_logger = getLogger()


def _create_registry_entries():
    """
    If you need to extend the application with a new search algorithm, this is the place where
    the new algorithm has to be registered.
    """
    return {
        "Naive-BFS": NaiveBreadthFirstSearch,
        "Smart-BFS": SmartBreadthFirstSearch,
        "Naive-DFS": NaiveDepthFirstSearch,
        "Smart-DFS": SmartDepthFirstSearch,
        "UCS": UnambiguousCandidateSearch,
    }


class NoSuchAlgorithmError(Exception):
    """
    Exception raised to indicate that search algorithm registry has been asked to
    instantiate an unknown search algorithm.
    """


class SearchAlgorithmRegistry:
    """
    This class represents the public API 

    Note:
        As this class provides only static methods, it does not make any sense to instantiate
        this class.
    """

    __entries = _create_registry_entries()

    @staticmethod
    def create_algorithm_instance(algorithm_name: str):
        """
        Creates and returns a new instance of the search algorithm with the given name.

        Args:
            algorithm_name:     The name of the search algorithm to be instantiated.

        Returns:
            The created instance of the specified search algorithm.

        Raises:
            NoSuchAlgorithmError    If there is no search algorithm with the given name.
        """
        if algorithm_name not in SearchAlgorithmRegistry.__entries:
            _logger.error("No algorithm with the name %s found", algorithm_name)
            message = "Unknown search algorithm '{0}' has been requested. Available search algorithms: {1}."
            message = message.format(algorithm_name, SearchAlgorithmRegistry.get_available_algorithms())
            raise NoSuchAlgorithmError(message)
        algorithm_class = SearchAlgorithmRegistry.__entries[algorithm_name]
        _logger.info("Going to instantiate %s (name = %s)", algorithm_class.__name__, algorithm_name)
        return algorithm_class()


    @staticmethod
    def get_available_algorithms() -> Tuple[str, ...]:
        """
        Creates and returns a tuple containing the names of all search algorithms this
        class can instantiate.

        Returns:
            Tuple containing the names of all search algorithms this class is aware of.
            Each of the names contained in the returned tuple can be used as algorithm
            name and passed to the create_algorithm_instance method.
        """
        return tuple(SearchAlgorithmRegistry.__entries.keys())
