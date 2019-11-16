import json
import unittest

from app import app
from tests.k8_kat.base.k8_kat_test import K8katTest


class TestDeploymentsController(K8katTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestDeploymentsController, cls).setUpClass()
    cls.create_dep('n1', 'd1', [('l1', 'v1')])
    cls.create_dep('n1', 'd2', [('l2', 'v2')])

    cls.create_dep('n2', 'd1', [('l1', 'v1'), ('c', 'c')])
    cls.create_dep_svc('n2', 'd1')

    cls.create_dep('n3', 'd3', [('l3', 'v3'), ('c', 'c')])

  def test_index_no_assocs(self):
    resp = app.test_client().get('/api/deployments')
    actual = json.loads(resp.data)['data']
    self.assertEqual(len(actual), 4)

    arg = 'ns_filter_type=whitelist&ns_filters=n1'
    resp = app.test_client().get(f'/api/deployments?{arg}')
    self.assertCountEqual(names(resp), ['d1', 'd2'])

    arg = 'ns_filter_type=whitelist&ns_filters=n1,n3'
    resp = app.test_client().get(f'/api/deployments?{arg}')
    self.assertCountEqual(names(resp), ['d1', 'd2', 'd3'])

    arg = 'ns_filter_type=blacklist&ns_filters=n1,n2'
    resp = app.test_client().get(f'/api/deployments?{arg}')
    self.assertCountEqual(names(resp), ['d3'])

    arg = 'ns_filter_type=whitelist&ns_filters=n1'
    arg2 = 'lb_filter_type=whitelist&lb_filters=l1:v1'
    resp = app.test_client().get(f'/api/deployments?{arg}&{arg2}')
    self.assertCountEqual(names(resp), ['d1'])

    arg = 'ns_filter_type=whitelist&ns_filters=n1,n2,n3'
    arg2 = 'lb_filter_type=whitelist&lb_filters=c:c,l3:v3'
    resp = app.test_client().get(f'/api/deployments?{arg}&{arg2}')
    self.assertCountEqual(names(resp), ['d3'])

  def test_index_with_assocs(self):
    arg = 'ns_filter_type=whitelist&ns_filters=n3'
    arg2 = '&svcs=false'
    resp = app.test_client().get(f'/api/deployments?{arg}&{arg2}')
    self.assertIsNone(dep_called(resp, 'd3').get('pods'))

    arg = 'ns_filter_type=whitelist&ns_filters=n3'
    arg2 = '&svcs=true'
    resp = app.test_client().get(f'/api/deployments?{arg}&{arg2}')
    self.assertEqual(dep_called(resp, 'd3')['svcs'], [])

    arg = 'ns_filter_type=whitelist&ns_filters=n2'
    arg2 = '&svcs=true'
    resp = app.test_client().get(f'/api/deployments?{arg}&{arg2}')
    self.assertEqual(dep_called_svcs_names(resp, 'd1'), ['d1'])

    self.ensure_no_pods('n2')
    arg = 'ns_filter_type=whitelist&ns_filters=n2'
    arg2 = '&svcs=true&pods=true'
    resp = app.test_client().get(f'/api/deployments?{arg}&{arg2}')
    print(dep_called_pods_labels(resp, 'd1'))
    self.assertEqual(dep_called_pods_labels(resp, 'd1'), [dict(app='d1')])
    self.assertEqual(dep_called_svcs_names(resp, 'd1'), ['d1'])

  # def test_across_namespaces(self):
  #   resp = app.test_client().get('/api/deployments/across_namespaces')
  #   actual = json.loads(resp.data)['data']
  #   exp_d1 = dict(name='d1', namespaces=['n1', 'n2'])
  #   exp_d2 = dict(name='d2', namespaces=['n1'])
  #   exp_d3 = dict(name='d3', namespaces=['n3'])
  #   print(actual)
  #   print([exp_d1, exp_d2, exp_d3])
  #   self.assertCountEqual(actual, [exp_d1, exp_d2, exp_d3])


if __name__ == '__main__':
    unittest.main()

def names(resp):
  return [d['name'] for d in json.loads(resp.data)['data']]

def dep_called(resp, name):
  ser_deps = json.loads(resp.data)['data']
  return [d for d in ser_deps if d['name'] == name][0]

def dep_called_svcs_names(resp, name):
  return [s['name'] for s in dep_called(resp, name)['svcs']]

def dep_called_pods_labels(resp, name):
  return [p['labels'] for p in dep_called(resp, name)['pods']]
