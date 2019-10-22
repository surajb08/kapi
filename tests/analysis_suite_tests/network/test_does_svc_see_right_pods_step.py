import unittest

from actions.image_reloader import ImageReloader
from analysis_suites.network.does_svc_see_pods_step import DoesSvcSeePodsStep
from analysis_suites.network.does_svc_see_right_pods_step import DoesSvcSeeRightPodsStep
from analysis_suites.network.is_svc_visible_step import IsSvcVisibleStep
from tests.analysis_suite_tests.network.base import Base

class DoesSvcSeeRightPodsStepTest(Base):

  @classmethod
  def setUpClass(cls):
    super().stdSetUpClass(DoesSvcSeeRightPodsStep)

  def test_positive(self):
    self.step.perform()
    print(self.step.outputs)
    self.post_test_positive()

  # def _test_negative(self):
  #   self.step.perform()
  #   self.post_test_negative()
  #
  # def test_negative(self):
  #   self.mock_step_prop("agg_addresses", [["foo"]], self._test_negative)

if __name__ == '__main__':
  unittest.main()