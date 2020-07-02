import unittest
from src import main

class TestComparePolicies(unittest.TestCase):
  def test_same_policy(self):
    """
    Test that function can compare same lists
    """
    list1 = ["a", "b", "c"]
    list2 = ["a", "b", "c"]
    result = main.compare_policies(list1, list2)
    self.assertFalse(result)

  def test_different_policy(self):
    """
    Test that function can see differences
    """
    list1 = ["a", "b", "c"]
    list2 = ["d", "e", "f"]
    result = main.compare_policies(list1, list2)
    self.assertTrue(result)
    
if __name__ == '__main__':
    unittest.main()