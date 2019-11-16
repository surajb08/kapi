import unittest

from analysis_suites.network.does_svc_see_right_pods_step import DoesSvcSeeRightPodsStep
from tests.analysis_suite_tests.network.base import Base


class DoesSvcSeeRightPodsStepTest(Base):

  @classmethod
  def setUpClass(cls):
    super().stdSetUpClass(DoesSvcSeeRightPodsStep)

  def test_positive(self):
    self.step.perform()
    print(self.step.outputs)
    self.post_test_positive()


if __name__ == '__main__':
  unittest.main()
