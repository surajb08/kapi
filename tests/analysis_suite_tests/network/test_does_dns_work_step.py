import unittest

from analysis_suites.network.does_dns_work_step import DoesDnsWorkStep
from tests.analysis_suite_tests.network.base import Base

class TestDoesDnsWorkStep(Base):

  @classmethod
  def setUpClass(cls):
    super().stdSetUpClass(DoesDnsWorkStep)

  def test_positive(self):
    self.step.perform()
    super().post_test_positive()


if __name__ == '__main__':
  unittest.main()
