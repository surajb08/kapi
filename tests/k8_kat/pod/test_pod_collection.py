import unittest

from k8_kat.base.k8_kat import K8Kat
from tests.k8_kat.base.k8_kat_test import K8katTest

def names(query=None):
  query = query or K8Kat.pods()
  return query.pluck('name')

class TestPodCollection(K8katTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestPodCollection, cls).setUpClass()
    cls.ensure_no_pods()
    cls.create_pod('n1', 'p11', dict(l1='v1'))
    cls.create_pod('n1', 'p12', dict(l2='v2'))
    cls.create_pod('n2', 'p21', dict(l1='v1'))

  def test_delete_all(self):
    self.assertCountEqual(names(), ['p11', 'p12', 'p21'])
    K8Kat.pods().lbs_inc_each(l1='v1').delete_all()
    self.assertCountEqual(names(), ['p11', 'p12', 'p21'])


if __name__ == '__main__':
  unittest.main()
