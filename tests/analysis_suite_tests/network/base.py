import unittest

from analysis_suites.network.does_svc_connect_step import DoesSvcConnectStep
from helpers.dep_helper import DepHelper
from helpers.svc_helper import SvcHelper

TESTING_NS = "nectar-testing"
TESTING_DEP_NM = "simple-app-dep"
TESTING_SVC_NM = "simple-app-svc"

class Base(unittest.TestCase):

  @classmethod
  def stdSetUpClass(cls):
    cls.deployment = DepHelper.find(TESTING_NS, TESTING_DEP_NM)
    cls.service = SvcHelper.find(TESTING_NS, TESTING_SVC_NM)
    cls.step = DoesSvcConnectStep(
      from_port=cls.service.spec.ports[0].port,
      dep_ns=TESTING_NS,
      svc_name=TESTING_SVC_NM,
      dep_name=TESTING_DEP_NM,
    )

  def setUp(self):
    self.step.from_port = self.service.spec.ports[0].port

  def post_test_positive(self):
    self.assertTrue(self.step.outcome)
    self.ensure_copy_working()

  def post_test_negative(self):
    self.assertFalse(self.step.outcome)
    self.ensure_copy_working()

  def ensure_copy_working(self):
    self.assertIsNotNone(self.step.copy_bundle())
    self.assertIsNotNone(self.step.summary_copy())
    self.assertIsNotNone(self.step.commands_copy())
    self.assertIsNotNone(self.step.steps_copy())