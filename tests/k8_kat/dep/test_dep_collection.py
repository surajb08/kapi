import unittest

from k8_kat.base.k8_kat import K8kat
from tests.k8_kat.base.k8_kat_test import K8katTest


class TestDepCollection(K8katTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestDepCollection, cls).setUpClass()
    cls.create_dep('n1', 'd11', [('c', 'c'), ('l1', 'v1')])
    cls.create_dep('n1', 'd12', [('c', 'c'), ('l1', 'v2')])

    cls.create_dep('n2', 'd21', [('l1', 'v1')])
    cls.create_dep('n2', 'd22', [('l2', 'v2')])

  def test_names(self):
    result = K8kat.deps().ns('n1').names('d11').go()
    self.assertEqual([dep.name for dep in result], ['d11'])

    result = K8kat.deps().ns('n1').names('d11', 'd12').go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd12'])

    result = K8kat.deps().ns('n1', 'n2').names('d11', 'd22').go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd22'])

  def test_every_lb(self):
    result = K8kat.deps().ns('n1').every_lb([('c', 'c')]).go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd12'])

    result = K8kat.deps().ns('n1').every_lb([('l1', 'v1')]).go()
    self.assertCountEqual([dep.name for dep in result], ['d11'])

    result = K8kat.deps().ns('n1', 'n2').every_lb([('l1', 'v1')]).go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd21'])

    q = [('l1', 'v1'), ('c', 'c')]
    result = K8kat.deps().ns('n1', 'n2').every_lb(q).go()
    self.assertCountEqual([dep.name for dep in result], ['d11'])

    result = K8kat.deps().ns('n1', 'n2').every_lb([('c', 'c')]).go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd12'])

    q = [('x', 'y'), ('c', 'c')]
    result = K8kat.deps().ns('n1', 'n2').every_lb(q).go()
    self.assertCountEqual([dep.name for dep in result], [])

  def test_any_lb(self):
    result = K8kat.deps().ns('n1').any_lb([('c', 'c')]).go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd12'])

    q = [('l1', 'v1'), ('l1', 'v2')]
    result = K8kat.deps().ns('n1').any_lb(q).go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd12'])

    q = [('l1', 'v1'), ('l1', 'v2')]
    result = K8kat.deps().ns('n1', 'n2').any_lb(q).go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd12', 'd21'])


if __name__ == '__main__':
    unittest.main()
