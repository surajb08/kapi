import unittest

from app import app
from tests.k8_kat.base.k8_kat_test import K8katTest

class TestDeploymentsController(K8katTest):
  def test_across_namespaces(self):
    got = app.test_client().get('/api/deployments/across_namespaces')
    print(f"WOW {got}")


if __name__ == '__main__':
    unittest.main()


