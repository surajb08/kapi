import unittest

from k8_kat.base.k8_kat import K8Kat
from k8_kat.svc.kat_svc import KatSvc
from tests.k8_kat.base.k8_kat_test import K8katTest

class TestKatSvc(K8katTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestKatSvc, cls).setUpClass()
    cls.create_svc('n1', 's1')

  def setUp(self) -> None:
    self.subject: KatSvc = K8Kat.svcs().ns('n1').find('s1')

  def test_internal_ip(self):
    self.assertIsNotNone(self.subject.internal_ip)

  def test_from_port(self):
    self.assertEqual(self.subject.from_port, 80)

  def test_to_port(self):
    self.assertEqual(self.subject.to_port, 80)

  def test_short_dns(self):
    self.assertEqual(self.subject.short_dns, 's1.n1')

  def test_fqdn(self):
    self.assertEqual(self.subject.fqdn, 's1.n1.svc.cluster.local')


if __name__ == '__main__':
    unittest.main()
