import unittest

from k8_kat.base.k8_kat import K8kat
from k8_kat.dep.dep_composer import DepComposer
from tests.k8_kat.base.k8_kat_test import K8katTest

subject = DepComposer

class TestDepComposer(K8katTest):

  @classmethod
  def setUpClass(cls) -> None:
    cls.create_dep('n1', 'd11')
    cls.create_dep('n1', 'd12')
    cls.create_dep('n2', 'd21')

    cls.create_dep_svc('n1', 'd11')
    cls.create_dep_svc('n2', 'd21')

  def test_associate_svcs(self):
    deps = K8kat.deps().ns('n1').names('d12')
    subject.associate_svcs(deps)
    svc_names = [s.name for s in deps.go()[0].svcs()]
    print(f"{deps.go()[0].svcs()}")
    self.assertCountEqual(svc_names, ['d11'])


if __name__ == '__main__':
    unittest.main()
