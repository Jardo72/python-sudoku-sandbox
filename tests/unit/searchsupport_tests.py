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
This module is a collection of unit tests covering the functionality provided by the searchsupport module.
"""

from logging import basicConfig, INFO
from unittest import TestCase
from unittest.mock import Mock

from searchsupport import CandidateList, CandidateQueryMode, _CandidateCellExclusionLogic, _CandidateValueExclusionLogic, _ExclusionLogic, _ExclusionOutcome, _RegionCandidateCells, UnambiguousCandidate


class UnambiguousCandidateTest(TestCase):
    """
    Test fixture aimed at the UnambiguousCandidate class.
    """

    def test_unambiguous_candidate_is_equal_to_itself(self):
        candidate = UnambiguousCandidate(row = 3, column = 7, value = 5)
        self.assertEqual(candidate, candidate)


    def test_two_unambiguous_candidate_instances_are_equal_if_they_have_equal_row_and_column_and_value(self):
        candidate_one = UnambiguousCandidate(row = 7, column = 4, value = 1)
        candidate_two = UnambiguousCandidate(row = 7, column = 4, value = 1)

        self.assertEqual(candidate_one, candidate_two)
        self.assertEqual(candidate_two, candidate_one)


    def test_unambiguous_candidate_is_not_equal_to_none(self):
        candidate = UnambiguousCandidate(row = 4, column = 1, value = 3)
        self.assertNotEqual(candidate, None)


    def test_unambiguous_candidate_is_not_equal_to_instance_of_other_class(self):
        candidate = UnambiguousCandidate(row = 9, column = 2, value = 6)
        self.assertNotEqual(candidate, "dummy")


    def test_two_unambiguous_candidate_instances_are_not_equal_if_they_have_identical_value_and_row_but_distinct_column(self):
        candidate_one = UnambiguousCandidate(row = 3, column = 9, value = 4)
        candidate_two = UnambiguousCandidate(row = 3, column = 8, value = 4)

        self.assertNotEqual(candidate_one, candidate_two)
        self.assertNotEqual(candidate_two, candidate_one)


    def test_two_unambiguous_candidate_instances_are_not_equal_if_they_have_identical_value_and_column_but_distinct_row(self):
        candidate_one = UnambiguousCandidate(row = 1, column = 5, value = 2)
        candidate_two = UnambiguousCandidate(row = 3, column = 5, value = 2)

        self.assertNotEqual(candidate_one, candidate_two)
        self.assertNotEqual(candidate_two, candidate_one)


    def test_two_unambiguous_candidate_instances_are_not_equal_if_they_have_identical_row_and_column_but_distinct_value(self):
        candidate_one = UnambiguousCandidate(row = 4, column = 7, value = 2)
        candidate_two = UnambiguousCandidate(row = 4, column = 7, value = 3)

        self.assertNotEqual(candidate_one, candidate_two)
        self.assertNotEqual(candidate_two, candidate_one)


    def test_unambiguous_candidate_provides_proper_cell_address(self):
        candidate = UnambiguousCandidate(row = 6, column = 4, value = 7)
        self.assertEqual((6, 4), candidate.cell_address)

        candidate = UnambiguousCandidate(row = 0, column = 5, value = 3)
        self.assertEqual((0, 5), candidate.cell_address)


class CandidateListTest(TestCase):
    """
    Test fixture aimed at the CandidateList class.
    """

    def test_candidate_list_is_equal_to_itself(self):
        candidate_list = CandidateList(row = 3, column = 2, values = [1, 7, 9])
        self.assertEqual(candidate_list, candidate_list)


    def test_two_candidate_list_instances_are_equal_if_they_have_identical_cell_address_and_values(self):
        candidate_list_one = CandidateList(row = 3, column = 2, values = [1, 7, 9])
        candidate_list_two = CandidateList(row = 3, column = 2, values = [1, 7, 9])
        self.assertEqual(candidate_list_one, candidate_list_two)
        self.assertEqual(candidate_list_two, candidate_list_one)


    def test_two_candidate_list_instances_are_equal_if_they_have_identical_cell_address_and_values_even_if_the_order_of_values_is_distinct(self):
        candidate_list_one = CandidateList(row = 8, column = 5, values = [1, 7, 9])
        candidate_list_two = CandidateList(row = 8, column = 5, values = [9, 7, 1])
        self.assertEqual(candidate_list_one, candidate_list_two)
        self.assertEqual(candidate_list_two, candidate_list_one)


    def test_candidate_list_is_not_equal_to_none(self):
        candidate_list = CandidateList(row = 3, column = 2, values = [1, 7, 9])
        self.assertNotEqual(candidate_list, None)


    def test_candidate_list_is_not_equal_to_instance_of_other_class(self):
        candidate_list = CandidateList(row = 3, column = 2, values = [1, 7, 9])
        self.assertNotEqual(candidate_list, "dummy")


    def test_two_candidate_list_instances_are_not_equal_if_they_have_identical_cell_address_but_distinct_values(self):
        candidate_list_one = CandidateList(row = 3, column = 2, values = [1, 7])
        candidate_list_two = CandidateList(row = 3, column = 2, values = [1, 4, 9])
        self.assertNotEqual(candidate_list_one, candidate_list_two)
        self.assertNotEqual(candidate_list_two, candidate_list_one)


    def test_two_candidate_list_instances_are_not_equal_if_they_have_identical_column_and_values_but_distinct_row(self):
        candidate_list_one = CandidateList(row = 3, column = 2, values = [1, 7, 9])
        candidate_list_two = CandidateList(row = 4, column = 2, values = [1, 7, 9])
        self.assertNotEqual(candidate_list_one, candidate_list_two)
        self.assertNotEqual(candidate_list_two, candidate_list_one)


    def test_two_candidate_list_instances_are_not_equal_if_they_have_identical_row_and_values_but_distinct_column(self):
        candidate_list_one = CandidateList(row = 4, column = 9, values = [3, 6, 7, 9])
        candidate_list_two = CandidateList(row = 4, column = 2, values = [3, 6, 7, 9])
        self.assertNotEqual(candidate_list_one, candidate_list_two)
        self.assertNotEqual(candidate_list_two, candidate_list_one)


    def test_length_of_candidate_list_reflects_the_number_of_candidate_values(self):
        candidate_list = CandidateList(row = 3, column = 2, values = [1, 7, 9])
        self.assertEqual(3, len(candidate_list))

        candidate_list = CandidateList(row = 3, column = 2, values = [2, 3, 7, 8, 9])
        self.assertEqual(5, len(candidate_list))


    def test_candidate_list_provides_proper_cell_address(self):
        candidate_list = CandidateList(row = 3, column = 2, values = [1, 7, 9])
        self.assertEqual((3, 2), candidate_list.cell_address)

        candidate_list = CandidateList(row = 8, column = 0, values = [2, 3, 7, 8, 9])
        self.assertEqual((8, 0), candidate_list.cell_address)


class CandidateValueExclusionLogicTest(TestCase):
    """
    Test fixture aimed at the CandidateValueExclusionLogic class. When designing the
    test cases, I wanted to ensure complete coverage of various aspects:
    * Various kinds of exclusion (pure row exclusion, pure column exclusion, pure region
      exclusion, various combinations like row and column exclusion).
    * Equivalence classes and (implicit) boundary values (i.e. top/bottom row,
      leftmost/rightmost column, regions).
    * All valid cell values.
    """

    def setUp(self):
        self._exclusion_logic = _CandidateValueExclusionLogic()


    def test_pure_row_exclusion_in_topmost_row_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        | 9 6 5 | 8 7 4 |   1 3 |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 2 has to be identified as unambiguous candidate
        for the cell [0; 6].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 2, value = 5)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 0, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 7, value = 1)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 4, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 1, value = 6)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 8, value = 3)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 3, value = 8)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 0, column = 5, value = 4)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 0, column = 6, value = 2) in candidate_list)


    def test_pure_row_exclusion_in_bottom_row_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        | 7 6   | 2 4 8 | 1 3 9 |
        +-------+-------+-------+

        For the grid above, the value 5 has to be identified as unambiguous candidate
        for the cell [8; 2].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 7, value = 3)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 0, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 3, value = 2)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 8, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 1, value = 6)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 6, value = 1)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 4, value = 4)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 8, column = 5, value = 8)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 8, column = 2, value = 5) in candidate_list)


    def test_pure_column_exclusion_in_leftmost_column_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        | 3     |       |       |
        | 7     |       |       |
        | 1     |       |       |
        +-------+-------+-------+
        | 9     |       |       |
        | 2     |       |       |
        | 6     |       |       |
        +-------+-------+-------+
        |       |       |       |
        | 5     |       |       |
        | 8     |       |       |
        +-------+-------+-------+

        For the grid above, the value 4 has to be identified as unambiguous candidate
        for the cell [6; 0].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 0, value = 3)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 0, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 4, column = 0, value = 2)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 3, column = 0, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 5, column = 0, value = 6)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 2, column = 0, value = 1)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 7, column = 0, value = 5)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 8, column = 0, value = 8)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 6, column = 0, value = 4) in candidate_list)


    def test_pure_column_exclusion_in_rightmost_column_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |     2 |
        |       |       |     7 |
        |       |       |     5 |
        +-------+-------+-------+
        |       |       |     9 |
        |       |       |     4 |
        |       |       |     3 |
        +-------+-------+-------+
        |       |       |     6 |
        |       |       |     8 |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 1 has to be identified as unambiguous candidate
        for the cell [8; 8].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 5, column = 8, value = 3)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 8, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 8, value = 2)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 3, column = 8, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 6, column = 8, value = 6)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 4, column = 8, value = 4)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 2, column = 8, value = 5)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 7, column = 8, value = 8)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 8, column = 8, value = 1) in candidate_list)


    def test_pure_region_exclusion_in_upper_left_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        | 3 1 6 |       |       |
        | 9 2 4 |       |       |
        | 8   5 |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 7 has to be identified as unambiguous candidate
        for the cell [2; 1].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 0, value = 3)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 2, value = 4)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 1, value = 2)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 0, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 2, value = 6)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 1, value = 1)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 2, column = 2, value = 5)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 2, column = 0, value = 8)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 2, column = 1, value = 7) in candidate_list)


    def test_pure_region_exclusion_in_upper_right_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       | 9 1   |
        |       |       | 2 7 3 |
        |       |       | 4 5 8 |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 6 has to be identified as unambiguous candidate
        for the cell [0; 8].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 7, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 8, value = 3)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 6, value = 2)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 6, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 2, column = 6, value = 4)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 7, value = 1)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 2, column = 7, value = 5)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 2, column = 8, value = 8)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 0, column = 8, value = 6) in candidate_list)


    def test_pure_region_exclusion_in_bottom_left_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        | 9 1 5 |       |       |
        | 6   2 |       |       |
        | 3 4 7 |       |       |
        +-------+-------+-------+

        For the grid above, the value 8 has to be identified as unambiguous candidate
        for the cell [7; 1].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 1, value = 4)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 6, column = 1, value = 1)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 7, column = 0, value = 6)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 7, column = 2, value = 2)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 6, column = 0, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 2, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 6, column = 2, value = 5)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 8, column = 0, value = 3)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 7, column = 1, value = 8) in candidate_list)


    def test_pure_region_exclusion_in_bottom_right_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       | 5 7 1 |
        |       |       | 8 2 9 |
        |       |       | 6 4   |
        +-------+-------+-------+

        For the grid above, the value 3 has to be identified as unambiguous candidate
        for the cell [8; 8].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 6, value = 6)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 7, column = 6, value = 8)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 6, column = 8, value = 1)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 7, column = 8, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 7, value = 4)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 6, column = 7, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 6, column = 6, value = 5)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 7, column = 7, value = 2)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 8, column = 8, value = 3) in candidate_list)


    def test_combination_of_row_and_column_exclusion_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       | 9     |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       | 2     |       |
        |   3   |     5 | 1   8 |
        |       |       |       |
        +-------+-------+-------+
        |       | 4     |       |
        |       | 7     |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 6 has to be identified as unambiguous candidate
        for the cell [4; 3].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 4, column = 5, value = 5)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 4, column = 8, value = 8)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 4, column = 6, value = 1)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 3, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 6, column = 3, value = 4)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 7, column = 3, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 4, column = 1, value = 3)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 3, column = 3, value = 2)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 4, column = 3, value = 6) in candidate_list)


    def test_combination_of_row_and_region_exclusion_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        | 7   3 |     2 |   8 5 |
        |       |       |   1   |
        |       |       | 6   4 |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 9 has to be identified as unambiguous candidate
        for the cell [3; 6].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 3, column = 8, value = 5)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 3, column = 7, value = 8)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 4, column = 7, value = 1)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 5, column = 6, value = 6)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 5, column = 8, value = 4)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 3, column = 0, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 3, column = 2, value = 3)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 3, column = 5, value = 2)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 3, column = 6, value = 9) in candidate_list)


    def test_combination_of_column_and_region_exclusion_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       | 3     |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       | 7   9 |       |
        |       |   5   |       |
        |       | 4 8   |       |
        +-------+-------+-------+
        |       | 6     |       |
        |       | 2     |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 1 has to be identified as unambiguous candidate
        for the cell [4; 3].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 3, column = 5, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 5, column = 4, value = 8)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 4, column = 4, value = 5)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 6, column = 3, value = 6)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 5, column = 3, value = 4)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 3, column = 3, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 3, value = 3)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 7, column = 3, value = 2)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 4, column = 3, value = 1) in candidate_list)


    def test_combination_of_row_and_column_and_region_exlusion_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |       |
        |     4 |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |     1 |       |       |
        |       |       |       |
        +-------+-------+-------+
        |   2   |   7   |     6 |
        | 5     |       |       |
        |   9 3 |       |       |
        +-------+-------+-------+

        For the grid above, the value 8 has to be identified as unambiguous candidate
        for the cell [6; 2].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 1, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 4, column = 2, value = 1)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 7, column = 0, value = 5)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 6, column = 8, value = 6)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 2, value = 4)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 6, column = 4, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 2, value = 3)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 6, column = 1, value = 2)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 6, column = 2, value = 8) in candidate_list)


    def test_candidates_for_first_undefined_cell_reflect_exclusion(self):
        """
        +-------+-------+-------+
        |       | 7     |       |
        |   9   |       |       |
        |   4   |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        | 2     |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the values 1, 3, 5, 6 and 8 have to be identified as candidates
        for the cell [0; 0], which should be identified as the first undefined cell.
        """
        self._exclusion_logic.apply_and_exclude_cell_value(row = 0, column = 3, value = 7)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 5, column = 0, value = 2)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 1, column = 1, value = 9)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 2, column = 1, value = 4)

        actual_candidate_list = self._exclusion_logic.get_undefined_cell_candidates(CandidateQueryMode.FIRST_UNDEFINED_CELL)
        expected_candidate_list = CandidateList(row = 0, column = 0, values = [1, 3, 5, 6, 8])
        self.assertEqual(actual_candidate_list, expected_candidate_list)


    def test_candidates_for_undefined_cell_with_least_candidates_reflect_exclusion(self):
        """
        +-------+-------+-------+
        |       | 7     |       |
        |   9   |       |     3 |
        |   4   |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |     2 |
        | 2     |       |       |
        +-------+-------+-------+
        |       |       | 7     |
        |       |       |     1 |
        |     5 |     9 |       |
        +-------+-------+-------+

        For the grid above, the values 4, 6 and 8 have to be identified as candidates
        for the cell [8; 8], which should be identified as the undefined cells with
        least candidate.
        """
        self._exclusion_logic.apply_and_exclude_cell_value(row = 0, column = 3, value = 7)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 1, column = 1, value = 9)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 1, column = 8, value = 3)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 2, column = 1, value = 4)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 4, column = 8, value = 2)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 5, column = 0, value = 2)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 6, column = 6, value = 7)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 7, column = 8, value = 1)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 8, column = 2, value = 5)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 8, column = 5, value = 9)

        actual_candidate_list = self._exclusion_logic.get_undefined_cell_candidates(CandidateQueryMode.UNDEFINED_CELL_WITH_LEAST_CANDIDATES)
        expected_candidate_list = CandidateList(row = 8, column = 8, values = [4, 6, 8])
        self.assertEqual(actual_candidate_list, expected_candidate_list)


    def test_no_value_is_applicable_to_cell_whose_value_has_been_already_set(self):
        self._exclusion_logic.apply_and_exclude_cell_value(row = 3, column = 2, value = 5)
        for value in range(1, 10):
            candidate = UnambiguousCandidate(row = 3, column = 2, value = value)
            self.assertFalse(self._exclusion_logic.is_applicable(candidate))


    def test_applicability_of_value_reflects_former_exclusions(self):
        self._exclusion_logic.apply_and_exclude_cell_value(row = 0, column = 5, value = 9)
        self.assertTrue(self._exclusion_logic.is_applicable(UnambiguousCandidate(row = 0, column = 4, value = 8)))
        self.assertFalse(self._exclusion_logic.is_applicable(UnambiguousCandidate(row = 0, column = 4, value = 9)))

        self._exclusion_logic.apply_and_exclude_cell_value(row = 2, column = 5, value = 6)
        self.assertTrue(self._exclusion_logic.is_applicable(UnambiguousCandidate(row = 1, column = 5, value = 3)))
        self.assertFalse(self._exclusion_logic.is_applicable(UnambiguousCandidate(row = 1, column = 5, value = 6)))

        self._exclusion_logic.apply_and_exclude_cell_value(row = 3, column = 0, value = 5)
        self.assertTrue(self._exclusion_logic.is_applicable(UnambiguousCandidate(row = 5, column = 1, value = 3)))
        self.assertFalse(self._exclusion_logic.is_applicable(UnambiguousCandidate(row = 5, column = 1, value = 5)))


    def test_number_of_applicable_values_reflects_exclusion(self):
        self.assertEqual(9, self._exclusion_logic.get_applicable_value_count(row = 0, column = 0))

        self._exclusion_logic.apply_and_exclude_cell_value(row = 0, column = 0, value = 1)
        self.assertEqual(0, self._exclusion_logic.get_applicable_value_count(row = 0, column = 0))
        self.assertEqual(8, self._exclusion_logic.get_applicable_value_count(row = 0, column = 1))
        self.assertEqual(8, self._exclusion_logic.get_applicable_value_count(row = 1, column = 0))

        self._exclusion_logic.apply_and_exclude_cell_value(row = 1, column = 1, value = 3)
        self.assertEqual(0, self._exclusion_logic.get_applicable_value_count(row = 1, column = 1))
        self.assertEqual(7, self._exclusion_logic.get_applicable_value_count(row = 0, column = 1))
        self.assertEqual(7, self._exclusion_logic.get_applicable_value_count(row = 1, column = 0))

        self._exclusion_logic.apply_and_exclude_cell_value(row = 2, column = 2, value = 9)
        self.assertEqual(0, self._exclusion_logic.get_applicable_value_count(row = 2, column = 2))
        self.assertEqual(6, self._exclusion_logic.get_applicable_value_count(row = 0, column = 1))
        self.assertEqual(6, self._exclusion_logic.get_applicable_value_count(row = 1, column = 0))


    def test_clone_reflects_the_state_of_the_original_when_candidates_are_requested(self):
        """
        +-------+-------+-------+
        | 2     | 7     | 1     |
        |     4 |       |     3 |
        |   8   |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |     2 |       |       |
        +-------+-------+-------+
        |       |       | 7     |
        |   3 5 |     9 |   2 4 |
        |       |       |       |
        +-------+-------+-------+

        For the grid above:
        * The cell [0; 1] is to be identified as the first undefined cell. The applicable
          candidates for that cell should be 5, 6, and 9.
        * The cell [7; 6] is to be identified as undefined cell with least candidates. The
          applicable candidates for that cell should be 6 and 8.
        A clone of the corresponding exclusion logic has to identify the same candidate
        values.
        """
        self._exclusion_logic.apply_and_exclude_cell_value(row = 0, column = 0, value = 2)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 0, column = 3, value = 7)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 0, column = 6, value = 1)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 1, column = 2, value = 4)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 1, column = 8, value = 3)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 2, column = 1, value = 8)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 6, column = 2, value = 2)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 6, column = 6, value = 7)

        self._exclusion_logic.apply_and_exclude_cell_value(row = 7, column = 1, value = 3)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 7, column = 2, value = 5)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 7, column = 5, value = 9)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 7, column = 7, value = 2)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 7, column = 8, value = 4)

        clone = self._exclusion_logic.copy()

        actual_candidate_list = clone.get_undefined_cell_candidates(CandidateQueryMode.FIRST_UNDEFINED_CELL)
        expected_candidate_list = CandidateList(row = 0, column = 1, values = [5, 6, 9])
        self.assertEqual(actual_candidate_list, expected_candidate_list)

        actual_candidate_list = clone.get_undefined_cell_candidates(CandidateQueryMode.UNDEFINED_CELL_WITH_LEAST_CANDIDATES)
        expected_candidate_list = CandidateList(row = 7, column = 6, values = [6, 8])
        self.assertEqual(actual_candidate_list, expected_candidate_list)


    def test_clone_reflects_the_state_of_the_original_when_further_exclusion_is_performed(self):
        """
        +-------+-------+-------+
        |       |       |       |
        |       |   5   |       |
        |       |       |       |
        +-------+-------+-------+
        |       | 1     |       |
        | 6     |     3 |   2   |
        |       | 7     |       |
        +-------+-------+-------+
        |       |   8   |       |
        |       |       |       |
        |       |   9   |       |
        +-------+-------+-------+

        For the grid above, value 4 is to be identified as unambiguous candidate for the
        cell [4; 4], even if half of the exclusion is performed with one instance of
        exclusion logic, and the other half is performed with a clone of the above mentioned
        instance. The unambiguous candidate is identified by the clone. The original instance
        cannot identify any unambiguous candidate.
        """
        self._exclusion_logic.apply_and_exclude_cell_value(row = 1, column = 4, value = 5)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 3, column = 3, value = 1)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 4, column = 0, value = 6)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 4, column = 7, value = 2)

        clone = self._exclusion_logic.copy()
        clone.apply_and_exclude_cell_value(row = 4, column = 5, value = 3)
        clone.apply_and_exclude_cell_value(row = 5, column = 3, value = 7)
        clone.apply_and_exclude_cell_value(row = 6, column = 4, value = 8)

        candidate_list = clone.apply_and_exclude_cell_value(row = 8, column = 4, value = 9)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 4, column = 4, value = 4) in candidate_list)


    def test_exclusion_in_clone_does_not_affect_the_original(self):
        """
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |     3 |       |
        |       | 7     |       |
        +-------+-------+-------+
        |       |   8   |       |
        |       |       |       |
        |       |   9   |       |
        +-------+-------+-------+

        For the grid above, the values 1, 2, 4, 5 and 6 have to be identified as candidates
        for the cell [3; 4]. The above mentioned cell should be identified as undefined cell
        with least candidates for the original exclusion logic instance, depsite of further
        exclusions performed with a clone of the exclusion logic.
        """
        self._exclusion_logic.apply_and_exclude_cell_value(row = 4, column = 5, value = 3)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 5, column = 3, value = 7)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 6, column = 4, value = 8)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 8, column = 4, value = 9)

        clone = self._exclusion_logic.copy()
        clone.apply_and_exclude_cell_value(row = 1, column = 4, value = 5)
        clone.apply_and_exclude_cell_value(row = 3, column = 3, value = 1)
        clone.apply_and_exclude_cell_value(row = 4, column = 7, value = 2)

        actual_candidate_list = self._exclusion_logic.get_undefined_cell_candidates(CandidateQueryMode.UNDEFINED_CELL_WITH_LEAST_CANDIDATES)
        expected_candidate_list = CandidateList(row = 3, column = 4, values = [1, 2, 4, 5, 6])
        self.assertEqual(actual_candidate_list, expected_candidate_list)


    def __test_that_exclusion_does_not_lead_to_unambiguous_candidate(self, row, column, value):
        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row, column, value)
        self.assertIs(candidate_list, None)


class RegionCandidateCellsTest(TestCase):
    """
    Test fixture aimed at the class _RegionCandidateCells.
    """

    def test_combination_of_row_and_column_exclusion_proper_candidate_is_found(self):
        """
        +-------+-------+-------+
        | 7     |       |       |
        |       |       |       |
        |       |       |     7 |
        +-------+-------+-------+
        |     7 |       |       |
        | 7     |       |       |
        |       |       | C     |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |   7   |
        +-------+-------+-------+

        For the grid above, the cell [5, 6] is the only cell in the middle right region (i.e. region
        with upper left cell [3, 6]) where the value 7 is applicable.
        """
        candidate_cells = _RegionCandidateCells(topmost_row = 3, leftmost_column = 6, value = 7)
        
        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 0, column = 0, value = 7)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND, exclusion_result)

        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 3, column = 2, value = 7)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND, exclusion_result)

        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 8, column = 7, value = 7)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND, exclusion_result)

        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 4, column = 0, value = 7)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND, exclusion_result)

        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 2, column = 8, value = 7)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_FOUND, exclusion_result)

        expected_unambiguous_candidate = UnambiguousCandidate(row = 5, column = 6, value = 7)
        actual_unambiguous_candidate = candidate_cells.get_single_remaining_applicable_cell()
        self.assertEqual(expected_unambiguous_candidate, actual_unambiguous_candidate)


    def test_combination_of_column_and_cell_exclusion_proper_candidate_is_found(self):
        """
        +-------+-------+-------+
        |       |       |       |
        |   2   |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |     2 |       |       |
        +-------+-------+-------+
        | 1     |       |       |
        | C     |       |       |
        | 4     |       |       |
        +-------+-------+-------+

        For the grid above, the cell [7, 0] is the only cell in the bottom left region (i.e. region
        with upper left cell [6, 0]) where the value 2 is applicable.
        """
        candidate_cells = _RegionCandidateCells(topmost_row = 6, leftmost_column = 0, value = 2)

        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 6, column = 0, value = 1)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND, exclusion_result)

        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 1, column = 1, value = 2)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND, exclusion_result)

        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 5, column = 2, value = 2)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND, exclusion_result)

        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 8, column = 0, value = 4)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_FOUND, exclusion_result)

        expected_unambiguous_candidate = UnambiguousCandidate(row = 7, column = 0, value = 2)
        actual_unambiguous_candidate = candidate_cells.get_single_remaining_applicable_cell()
        self.assertEqual(expected_unambiguous_candidate, actual_unambiguous_candidate)


    def test_combination_of_row_and_cell_exclusion_proper_candidate_is_found(self):
        """
        +-------+-------+-------+
        | 1 C 4 |       |       |
        |       |       |   8   |
        |       |   8   |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the cell [0, 1] is the only cell in the upper left region (i.e. region
        with upper left cell [0, 0]) where the value 8 is applicable.
        """
        candidate_cells = _RegionCandidateCells(topmost_row = 0, leftmost_column = 0, value = 8)

        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 0, column = 0, value = 1)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND, exclusion_result)

        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 1, column = 7, value = 8)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND, exclusion_result)

        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 2, column = 4, value = 8)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_NOT_FOUND, exclusion_result)

        exclusion_result = candidate_cells.apply_and_exclude_cell_value(row = 0, column = 2, value = 4)
        self.assertEqual(_ExclusionOutcome.UNAMBIGUOUS_CANDIDATE_FOUND, exclusion_result)

        expected_unambiguous_candidate = UnambiguousCandidate(row = 0, column = 1, value = 8)
        actual_unambiguous_candidate = candidate_cells.get_single_remaining_applicable_cell()
        self.assertEqual(expected_unambiguous_candidate, actual_unambiguous_candidate)


class CandidateCellExclusionLogicTest(TestCase):
    """
    Test fixture aimed at the CandidateCellExclusionLogic class. When designing the
    test cases, I wanted to ensure complete coverage of various aspects:
    * Exclusion of candidate cells in each of the nine regions.
    * All valid cell values.
    * Various kinds of exclusion (e.g. row and column, row and cells, column and cells).
    """

    def setUp(self):
        self._exclusion_logic = _CandidateCellExclusionLogic()


    def test_row_and_column_exclusion_with_cell_exclusion_in_upper_left_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |     9 |
        |     1 |       |       |
        |       | 9     |       |
        +-------+-------+-------+
        |   9   |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 9 has to be identified as unambiguous candidate for
        the cell [1; 0].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 8, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 2, column = 3, value = 9)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 3, column = 1, value = 9)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 1, column = 2, value = 1)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 1, column = 0, value = 9) in candidate_list)


    def test_row_and_column_exclusion_in_upper_middle_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |       |
        |       |       |     3 |
        |   3   |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       | 3     |       |
        |       |       |       |
        +-------+-------+-------+
        |       |     3 |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 3 has to be identified as unambiguous candidate for
        the cell [0; 4].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 2, column = 1, value = 3)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 8, value = 3)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 4, column = 3, value = 3)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 6, column = 5, value = 3)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 0, column = 4, value = 3) in candidate_list)


    def test_row_exclusion_with_cell_exclusion_in_upper_right_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       | 9 4   |
        | 2     |       |       |
        |       |     2 |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 2 has to be identified as unambiguous candidate for
        the cell [0; 8].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 0, value = 2)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 2, column = 3, value = 2)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 6, value = 9)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 0, column = 7, value = 4)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 0, column = 8, value = 2) in candidate_list)


    def test_column_exclusion_with_cell_exclusion_in_middle_left_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |     4 |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |   5   |       |       |
        |       |       |       |
        |   9   |       |       |
        +-------+-------+-------+
        |       |       |       |
        | 4     |       |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 4 has to be identified as unambiguous candidate for
        the cell [4; 1].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 2, value = 4)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 7, column = 0, value = 4)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 3, column = 1, value = 5)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 5, column = 1, value = 9)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 4, column = 1, value = 4) in candidate_list)


    def test_row_exclusion_with_cell_exclusion_in_middle_middle_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |   5   |       |       |
        |       | 2   7 |       |
        |       |       |     5 |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 5 has to be identified as unambiguous candidate for
        the cell [4; 4].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 3, column = 1, value = 5)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 5, column = 8, value = 5)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 4, column = 3, value = 2)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 4, column = 5, value = 7)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 4, column = 4, value = 5) in candidate_list)


    def test_row_and_column_exclusion_with_cell_exclusion_in_middle_right_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |   8   |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       | 5     |
        |       |       |       |
        |     8 |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |     8 |
        +-------+-------+-------+

        For the grid above, the value 8 has to be identified as unambiguous candidate for
        the cell [4; 6].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 7, value = 8)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 5, column = 2, value = 8)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 8, value = 8)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 3, column = 6, value = 5)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 4, column = 6, value = 8) in candidate_list)


    def test_row_and_column_exclusion_in_bottom_left_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |       |
        | 7     |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |     7 |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |   7   |
        |       |       |       |
        |       | 7     |       |
        +-------+-------+-------+

        For the grid above, the value 7 has to be identified as unambiguous candidate for
        the cell [7; 1].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 0, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 4, column = 2, value = 7)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 6, column = 7, value = 7)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 8, column = 3, value = 7)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 7, column = 1, value = 7) in candidate_list)


    def test_column_exclusion_with_cell_exclusion_in_bottom_middle_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |       |
        |       | 6     |       |
        |       |       |       |
        +-------+-------+-------+
        |       |   6   |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |     3 |       |
        |       |     8 |       |
        +-------+-------+-------+

        For the grid above, the value 6 has to be identified as unambiguous candidate for
        the cell [6; 5].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 1, column = 3, value = 6)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 3, column = 4, value = 6)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 7, column = 5, value = 3)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 8, column = 5, value = 8)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 6, column = 5, value = 6) in candidate_list)


    def test_row_and_column_exclusion_with_cell_exclusion_in_bottom_right_region_finds_proper_unambiguous_candidate(self):
        """
        +-------+-------+-------+
        |       |       |     1 |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+
        |       |       |   8   |
        |   1   |       |       |
        |       | 1     |       |
        +-------+-------+-------+

        For the grid above, the value 1 has to be identified as unambiguous candidate for
        the cell [6; 6].
        """
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 0, column = 8, value = 1)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 7, column = 1, value = 1)
        self.__test_that_exclusion_does_not_lead_to_unambiguous_candidate(row = 8, column = 3, value = 1)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 6, column = 7, value = 8)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 6, column = 6, value = 1) in candidate_list)


    def test_clone_reflects_the_state_of_the_original_when_further_exclusion_is_performed(self):
        """
        +-------+-------+-------+
        |       |       |       |
        |       | 4     |       |
        |       |       |       |
        +-------+-------+-------+
        |   4   |       |       |
        |       |     1 |       |
        |       |   7 2 |       |
        +-------+-------+-------+
        |       |       |       |
        |       |       |       |
        |       |       |       |
        +-------+-------+-------+

        For the grid above, the value 4 has to be identified as unambiguous candidate for
        the cell [4; 4], even if half of the exclusion is performed with one instance of
        exclusion logic, and the other half is performed with a clone of the above mentioned
        instance. The unambiguous candidate is identified by the clone. The original instance
        cannot identify any unambiguous candidate.
        """
        self._exclusion_logic.apply_and_exclude_cell_value(row = 1, column = 3, value = 4)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 4, column = 5, value = 1)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 5, column = 4, value = 7)

        clone = self._exclusion_logic.copy()
        clone.apply_and_exclude_cell_value(row = 3, column = 1, value = 4)

        candidate_list = clone.apply_and_exclude_cell_value(row = 5, column = 5, value = 2)
        self.assertEqual(len(candidate_list), 1)
        self.assertTrue(UnambiguousCandidate(row = 4, column = 4, value = 4) in candidate_list)


    def test_exclusion_in_clone_does_not_affect_the_original(self):
        """
        If a clone of exclusion logic is created after several exclusions, further exclusions
        performed upon the clone will not affect the original exclusion logic.
        """
        self._exclusion_logic.apply_and_exclude_cell_value(row = 1, column = 3, value = 4)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 4, column = 5, value = 1)
        self._exclusion_logic.apply_and_exclude_cell_value(row = 5, column = 4, value = 7)

        clone = self._exclusion_logic.copy()
        clone.apply_and_exclude_cell_value(row = 3, column = 1, value = 4)

        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row = 5, column = 5, value = 2)
        self.assertIsNone(candidate_list)


    def __test_that_exclusion_does_not_lead_to_unambiguous_candidate(self, row, column, value):
        candidate_list = self._exclusion_logic.apply_and_exclude_cell_value(row, column, value)
        self.assertIs(candidate_list, None)


class ExclusionLogicTest(TestCase):
    """
    Test fixture aimed at the class ExclusionLogic. 
    """

    def test_none_of_the_exclusions_finds_a_candidate_none_is_returned(self):
        value_exclusion_stub = Mock(_CandidateValueExclusionLogic)
        value_exclusion_stub.apply_and_exclude_cell_value.return_value = None

        cell_exclusion_stub = Mock(_CandidateCellExclusionLogic)
        cell_exclusion_stub.apply_and_exclude_cell_value.return_value = None

        exclusion_logic = _ExclusionLogic(value_exclusion_stub, cell_exclusion_stub)
        final_candidate_list = exclusion_logic.apply_and_exclude_cell_value(row = 3, column = 5, value = 2)
        self.assertIsNone(final_candidate_list)


    def test_value_exclusion_returns_non_empty_list_cell_exclusion_returns_none_value_exclusion_list_is_returned(self):
        value_exclusion_candidate_list = [
            UnambiguousCandidate(row = 8, column = 0, value = 4),
            UnambiguousCandidate(row = 8, column = 5, value = 7),
        ]
        value_exclusion_stub = Mock(_CandidateValueExclusionLogic)
        value_exclusion_stub.apply_and_exclude_cell_value.return_value = value_exclusion_candidate_list

        cell_exclusion_stub = Mock(_CandidateCellExclusionLogic)
        cell_exclusion_stub.apply_and_exclude_cell_value.return_value = None

        exclusion_logic = _ExclusionLogic(value_exclusion_stub, cell_exclusion_stub)
        final_candidate_list = exclusion_logic.apply_and_exclude_cell_value(row = 3, column = 5, value = 2)
        self.assertListEqual(value_exclusion_candidate_list, final_candidate_list)


    def test_cell_exclusion_returns_non_empty_list_value_exclusion_returns_none_cell_exclusion_list_is_returned(self):
        value_exclusion_stub = Mock(_CandidateValueExclusionLogic)
        value_exclusion_stub.apply_and_exclude_cell_value.return_value = None

        cell_exclusion_candidate_list = [
            UnambiguousCandidate(row = 8, column = 0, value = 4),
            UnambiguousCandidate(row = 8, column = 5, value = 7),
        ]
        cell_exclusion_stub = Mock(_CandidateCellExclusionLogic)
        cell_exclusion_stub.apply_and_exclude_cell_value.return_value = cell_exclusion_candidate_list

        exclusion_logic = _ExclusionLogic(value_exclusion_stub, cell_exclusion_stub)
        final_candidate_list = exclusion_logic.apply_and_exclude_cell_value(row = 3, column = 5, value = 2)
        self.assertListEqual(cell_exclusion_candidate_list, final_candidate_list)


    def test_both_exclusions_return_non_empty_list_union_of_both_lists_is_returned(self):
        value_exclusion_candidate_list = [
            UnambiguousCandidate(row = 2, column = 3, value = 9),
            UnambiguousCandidate(row = 5, column = 1, value = 2),
            UnambiguousCandidate(row = 8, column = 7, value = 6),
        ]
        value_exclusion_stub = Mock(_CandidateValueExclusionLogic)
        value_exclusion_stub.apply_and_exclude_cell_value.return_value = value_exclusion_candidate_list

        cell_exclusion_candidate_list = [
            UnambiguousCandidate(row = 8, column = 0, value = 4),
            UnambiguousCandidate(row = 7, column = 5, value = 1),
        ]
        cell_exclusion_stub = Mock(_CandidateCellExclusionLogic)
        cell_exclusion_stub.apply_and_exclude_cell_value.return_value = cell_exclusion_candidate_list

        exclusion_logic = _ExclusionLogic(value_exclusion_stub, cell_exclusion_stub)
        final_candidate_list = exclusion_logic.apply_and_exclude_cell_value(row = 3, column = 5, value = 2)
        self.assertListEqual(value_exclusion_candidate_list + cell_exclusion_candidate_list, final_candidate_list)


    def test_both_exclusions_return_the_same_candidate_list_containing_duplicate_is_returned(self):
        value_exclusion_candidate_list = [
            UnambiguousCandidate(row = 8, column = 0, value = 4),
            UnambiguousCandidate(row = 8, column = 5, value = 7),
        ]
        value_exclusion_stub = Mock(_CandidateValueExclusionLogic)
        value_exclusion_stub.apply_and_exclude_cell_value.return_value = value_exclusion_candidate_list

        cell_exclusion_candidate_list = [
            UnambiguousCandidate(row = 8, column = 0, value = 4),
        ]
        cell_exclusion_stub = Mock(_CandidateCellExclusionLogic)
        cell_exclusion_stub.apply_and_exclude_cell_value.return_value = cell_exclusion_candidate_list

        exclusion_logic = _ExclusionLogic(value_exclusion_stub, cell_exclusion_stub)
        final_candidate_list = exclusion_logic.apply_and_exclude_cell_value(row = 3, column = 5, value = 2)
        self.assertListEqual(value_exclusion_candidate_list + cell_exclusion_candidate_list, final_candidate_list)


basicConfig(level = INFO,
        format = "%(asctime)s %(levelname)-8s %(module)-18s line %(lineno)-4d %(message)s",
        datefmt = "%d-%b-%Y %H:%M:%S",
        filename = "exclusiontest.log",
        filemode = "w")
