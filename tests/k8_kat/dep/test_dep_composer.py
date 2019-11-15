import unittest

from k8_kat.base.k8_kat import K8kat
from k8_kat.dep.dep_composer import DepComposer
from tests.k8_kat.base.k8_kat_test import K8katTest
from utils.utils import Utils

subject = DepComposer

class TestDepComposer(K8katTest):

  @classmethod
  def setUpClass(cls) -> None:
    cls.create_dep('n1', 'd0')
    cls.create_dep('n1', 'd11')
    cls.create_dep('n1', 'd12')
    cls.create_dep('n2', 'd21')

    cls.create_dep_svc('n1', 'd11')
    cls.create_dep_svc('n2', 'd21')

  @staticmethod
  def the_svc_names(deps):
    flat_svcs = Utils.flatten([dep.svcs() for dep in deps])
    return [svc.name for svc in flat_svcs]

  def test_associate_svcs(self):
    deps = K8kat.deps().ns('n1').names('d0').go()
    subject.associate_svcs(deps)
    self.assertEqual(self.the_svc_names(deps), [])

    deps = K8kat.deps().ns('n1').names('d11').go()
    subject.associate_svcs(deps)
    self.assertEqual(self.the_svc_names(deps), ['d11'])

    deps = K8kat.deps().ns('n1').names('d11', 'd12').go()
    subject.associate_svcs(deps)
    self.assertEqual(self.the_svc_names(deps), ['d11'])

    deps = K8kat.deps().ns('n1', 'n2').names('d11', 'd21').go()
    subject.associate_svcs(deps)
    self.assertEqual(self.the_svc_names(deps), ['d11', 'd21'])


if __name__ == '__main__':
    unittest.main()
