import unittest
from analysis_suites.network.is_svc_visible_step import IsSvcVisibleStep
from tests.analysis_suite_tests.network.base import Base

class IsSvcVisibleStepTest(Base):

  @classmethod
  def setUpClass(cls):
    super().stdSetUpClass(IsSvcVisibleStep)

  def test_positive(self):
    self.step.perform()
    super().post_test_positive()
    self.assertEqual(len(self.step.outputs), 2)

  def _test_negative(self):
    self.step.perform()
    self.post_test_negative()
    self.assertEqual(len(self.step.outputs), 0)

  def test_negative(self):
    self.mock_step_prop("fqdn", "foo", self._test_negative)


if __name__ == '__main__':
  unittest.main()
