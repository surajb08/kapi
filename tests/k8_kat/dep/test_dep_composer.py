import unittest

from tests.k8_kat.base.k8_kat_test import K8katTest


class TestDepComposer(K8katTest):

  @classmethod
  def setUpClass(cls) -> None:
    cls.create_dep('n1', 'd11')
    cls.create_dep('n1', 'd12')
    cls.create_dep('n2', 'd21')

    cls.create_dep_svc('n1', 'd11')
    cls.create_dep_svc('n2', 'd21')

  def test_associate_svcs(self):

    pass


if __name__ == '__main__':
    unittest.main()
