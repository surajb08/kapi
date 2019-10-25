import unittest

from analysis_suites.network.does_dns_work_step import DoesDnsWorkStep
from analysis_suites.network.is_svc_visible_step import IsSvcVisibleStep
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