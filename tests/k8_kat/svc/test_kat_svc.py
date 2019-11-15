from k8_kat.base.k8_kat import K8kat
from k8_kat.svc.kat_svc import KatSvc
from tests.k8_kat.base.k8_kat_test import K8katTest


class TestKatSvc(K8katTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestKatSvc, cls).setUpClass()
    cls.create_dep('n1', 'd1')
    cls.create_dep_svc('n1', 'd11')

  def setUp(self):
    self.subject: KatSvc = K8kat.svcs().ns('n1').find('d1')

  def test_internal_ip(self):
    self.assertIsNotNone(self.subject.internal_ip)

  def test_from_port(self):
    self.assertEqual(self.subject.from_port, 80)

  def test_to_port(self):
    self.assertEqual(self.subject.to_port, 80)

  def test_short_dns(self):
    self.assertEqual(self.subject.short_dns, 'd1.n1')

  def test_fqdn(self):
    self.assertEqual(self.subject.short_dns, 'd1.n1.svc.cluster.local')
