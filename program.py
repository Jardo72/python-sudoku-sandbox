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
This module is the entry point of the application. The functionality implemented in this
module is pretty simple, it only processes the command line arguments, reads and parses
the given puzzle, passes a search request to the search engine, and presents the search
result to the user. It's more or less glue code putting the components comprizing the
application together.
"""
 
from argparse import ArgumentParser, RawTextHelpFormatter
from logging import basicConfig, INFO
from logging.config import fileConfig
from os.path import isfile

from algorithmregistry import SearchAlgorithmRegistry, NoSuchAlgorithmError
from gridio import GridFormatter, PuzzleParser, InvalidInputError
from searchengine import SearchEngine, InvalidPuzzleError, SearchSummary


def _section_separator() -> str:
    return "=" * 75


def _epilog() -> str:
    return """
The following snippet illustrates the expected format of the input file
containing the puzzle to be solved.

+-------+-------+-------+
| 6     |     4 |   8 5 |
| 9 7   |   6 5 |       |
|   4 8 | 7 3   |       |
+-------+-------+-------+
|   8   | 2 4 7 |       |
|     6 |   8   | 5     |
|       | 1 5 6 |   4   |
+-------+-------+-------+
|       |   1 3 | 2 6   |
|       | 6 9   |   3 4 |
| 2 6   | 4     |     9 |
+-------+-------+-------+
    """


def _available_algorithms_as_csv() -> str:
    return ", ".join(map(lambda algorithm: "'" + algorithm + "'", SearchAlgorithmRegistry.get_available_algorithms()))


def _setup_logging():
    config_file = "logging-config.ini"
    if isfile(config_file):
        fileConfig(config_file)
        return

    basicConfig(level = INFO,
            format = "%(asctime)s %(levelname)-8s %(module)-18s line %(lineno)-4d %(message)s",
            datefmt = "%d-%b-%Y %H:%M:%S",
            filename = "python-sudoku-sandbox.log",
            filemode = "w")


def _create_command_line_arguments_parser() -> ArgumentParser:
    parser = ArgumentParser(description = "Python Sudoku Sandbox", epilog = _epilog(), formatter_class = RawTextHelpFormatter)

    # positional mandatory arguments
    parser.add_argument("input_file",
        help = "the name of the input file containing the puzzle to be solved")
    parser.add_argument("algorithm",
        help = "the name of the search algorithm to be used; available search algorithms are " + _available_algorithms_as_csv())

    # optional arguments
    parser.add_argument("-o", "--output",
        dest = "output_file",
        default = None,
        help = "the optional name of the output file the solution is to be written to")
    parser.add_argument("-t", "--timeout",
        dest = "timeout_sec",
        default = 60,
        help = "the optional timeout in seconds; 60 seconds is used as default if this argument is omitted",
        type = int)

    return parser


def _print_search_request(params):
    print()
    print(_section_separator())
    print("Input file:       {0}".format(params.input_file))
    print("Output file:      {0}".format(params.output_file))
    print("Search algorithm: {0}".format(params.algorithm))
    print("Timeout:          {0} sec".format(params.timeout_sec))
    print()


def _parse_command_line_arguments():
    parser = _create_command_line_arguments_parser()
    params = parser.parse_args()
    _print_search_request(params)
    return params


def _print_search_summary(search_summary: SearchSummary):
    print()
    print(_section_separator())
    print("Number of undefined cells in the puzzle: {0}".format(search_summary.original_puzzle.get_undefined_cell_count()))
    print("Search algorithm:                        {0}".format(search_summary.algorithm))
    print("Search outcome:                          {0}".format(search_summary.outcome))
    print("Search duration:                         {0} ms".format(search_summary.duration_millis))
    print("Number of tried cell values:             {0}".format(search_summary.cell_values_tried))
    print()
    GridFormatter.write_to_console(search_summary.final_grid)
    print()
    if not search_summary.final_grid.is_valid():
        print("ERROR!!!")
        print("The final grid is not valid, there is at least one duplicate in a row, in a column, or in a region.")
        print()


def _main():
    try:
        _setup_logging()
        command_line_arguments = _parse_command_line_arguments()
        cell_values = PuzzleParser.read_from_file(command_line_arguments.input_file)
        search_summary = SearchEngine.find_solution(cell_values, command_line_arguments.algorithm, command_line_arguments.timeout_sec)
        _print_search_summary(search_summary)
        if command_line_arguments.output_file is not None:
            GridFormatter.write_to_file(search_summary.final_grid, command_line_arguments.output_file)
    except InvalidInputError as e:
        print("Failed to parse the input file {0}: {1}".format(command_line_arguments.input_file, e))
    except (InvalidPuzzleError, NoSuchAlgorithmError) as e:
        print("Puzzle rejected by the search engine: {0}".format(e))
    except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
        print("I/O error: {0}".format(e))
    except (ValueError, RuntimeError) as e:
        print("Unexpected error has occured: {0}".format(e))
    finally:
        print()


if __name__ == "__main__":
    _main()
