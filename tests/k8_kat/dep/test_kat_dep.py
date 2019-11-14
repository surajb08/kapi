import unittest

from k8_kat.dep.kat_dep import KatDep
from tests.k8_kat.base.k8_kat_test import K8katTest


class TestKatDep(K8katTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestKatDep, cls).setUpClass()
    cls.nk_create_dep('n1', 'd1')
    cls.nk_label_dep('n1', 'd1', [('l1', 'v1')])

  def test_name(self):
    kat_dep = KatDep(self.read_dep('n1', 'd1'))
    self.assertEqual(kat_dep.name, 'd1')

  def test_labels(self):
    kat_dep = KatDep(self.read_dep('n1', 'd1'))
    self.assertEqual(kat_dep.labels, {'app': 'd1', 'l1': 'v1'})


if __name__ == '__main__':
    unittest.main()
