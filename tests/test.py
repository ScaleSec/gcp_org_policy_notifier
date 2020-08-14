import unittest
from src import main
import os

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
    Test that function can see differences between lists
    """
    list1 = ["a", "b", "c"]
    list2 = ["d", "e", "f"]
    result = main.compare_policies(list1, list2)
    self.assertTrue(result)


class TestPolicies(unittest.TestCase):
  def test_new_policies(self):
    """
    Test the function can get and return a policy as a dict
    """
    policy = main.list_org_policies()
    self.assertIsInstance(policy, dict)
    
  # todo: activate when separate environments are live
  # def test_old_policies(self):
  #   """
  #   Test the function can grab from GCS and return a list
  #   """
  #   policy = main.fetch_old_policies([])
  #   self.assertIsInstance(policy, list)

  # todo: activate when separate environments are live
  # def test_upload_policies(self):
  #   """
  #   Test that a policy can be uploaded to GCS
  #   """
  #   policy = main.list_org_policies()
  #   self.assertTrue(main.upload_policy_file(policy))

  def test_download_policies(self):
    """
    Test that a policy can be downloaded from GCS
    """
    policy = main.download_policy_file()
    self.assertIsInstance(policy, list)
    
if __name__ == '__main__':
  os.environ["ENVIRONMENT"] = "dev"
  unittest.main()