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
    Test that function can see differences between lists
    """
    list1 = ["a", "b", "c"]
    list2 = ["d", "e", "f"]
    result = main.compare_policies(list1, list2)
    self.assertTrue(result)


class TestPolicies(unittest.TestCase):
  def test_new_policies(self):
    """
    Test the function can get and return a policy as a list
    """
    policy = main.list_org_policies()
    self.assertIsInstance(policy, list)
    
  def test_old_policies(self):
    """
    Test the function can grab from GCS and return a list
    """
    policy = main.fetch_old_policies()
    self.assertIsInstance(policy, list)

  def test_upload_policies(self):
    """
    Test that a policy can be uploaded to GCS
    """
    policy = main.list_org_policies()
    self.assertTrue(main.upload_policy_file(policy))

  def test_download_policies(self):
    """
    Test that a policy can be downloaded from GCS
    """
    policy = main.download_policy_file()
    self.assertIsInstance(policy, list)

class TestSlack(unittest.TestCase):
  def test_get_webhook(self):
    """
    Test it can grab the slack webhook
    """
    self.assertTrue(main.fetch_slack_webhook())

  def test_post_to_slack(self):
    """
    Test it can post to slack
    """
    policy = ["unittest"]
    self.assertTrue(main.post_to_slack(policy))
    
if __name__ == '__main__':
    unittest.main()