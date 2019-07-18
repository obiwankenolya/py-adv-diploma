from diploma import *
import unittest
from unittest.mock import patch


class TestVkinder(unittest.TestCase):

    def test_user_id_and_length(self):
        with patch('diploma.input', side_effect=["6280082", ""]) as test_user_input:
            func_result1 = user1.get_partners()
            list1 = len(func_result1)
        with patch('diploma.input', side_effect=["baltsatu.olga", ""]) as test_user_input:
            func_result2 = user1.get_partners()
            list2 = len(func_result2)
        self.assertEqual(list1, list2)


if __name__ == '__main__':
    unittest.main()