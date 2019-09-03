import unittest

from pod_helper import PodHelper


class PodHelperSpec(unittest.TestCase):

  def test_is_pod_from_dep(self):
    dep_name = "pod-test-name"
    exp_true = [
      "pod-test-name-89un3-iio2un"
    ]
    exp_false = [

    ]

    for test_case in exp_true:
      dec = PodHelper.is_pod_from_dep()
      self.assertTrue()