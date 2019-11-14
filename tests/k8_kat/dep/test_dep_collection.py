from k8_kat.base.k8_kat import K8kat
from tests.k8_kat.base.k8_kat_test import K8katTest


class TestDepCollection(K8katTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestDepCollection, cls).setUpClass()
    # cls.k('create ns n2')

    cls.nk_create_dep('n1', 'd11', [('c', 'c'), ('l1', 'v1')])
    cls.nk_create_dep('n1', 'd12', [('c', 'c'), ('l1', 'v2')])

    cls.nk_create_dep('n2', 'd21', [('l1', 'v1')])
    cls.nk_create_dep('n2', 'd22', [('l2', 'v2')])

  @classmethod
  def tearDownClass(cls):
    super(TestDepCollection, cls).tearDownClass()
    cls.nk('delete deploy --all', 'n1')
    cls.nk('delete deploy --all', 'n2')
    # cls.k('delete ns/n2')

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

    q = [('l1', 'v1'), ('l1', 'v2'),('x','y')]
    result = K8kat.deps().ns('n1', 'n2').any_lb(q).go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd12', 'd21'])
    print(f"-------")
