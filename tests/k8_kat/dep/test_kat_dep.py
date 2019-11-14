import os
import unittest
from typing import Tuple

import app
from helpers.dep_helper import DepHelper as SafeDep
from helpers.kube_broker import broker


class TestKatDep(unittest.TestCase):

  @staticmethod
  def k(cmd: str):
    os.system(f"microk8s.kubectl {cmd}")

  @staticmethod
  def nk(cmd: str, ns: str = 'n1'):
    me.k(f"{cmd} -n {ns}")

  @staticmethod
  def read_dep(name, ns='n1'):
    return SafeDep.find(name, ns)

  @staticmethod
  def nk_create_dep(dep_name: str, img: str = 'nginx', ns=None):
    me.nk(f"create deploy {dep_name} --image {img}", ns)

  @staticmethod
  def nk_label_dep(dep_name: str,  label: Tuple[str, str], ns=None):
    me.nk(f"label deploy {dep_name} {label[0]}={label[1]}", ns)

  @staticmethod
  def create_basic_dep():
    me.nk_create_dep('d1', 'n1')
    me.nk_label_dep('d1', ('l1', 'v1'), 'n1')

  @classmethod
  def setUpClass(cls) -> None:
    filename = os.path.join(app.app.instance_path, 'ci-perms.yaml')
    filename = filename.replace('/instance', '')
    cls.k(f"apply -f {filename}")
    cls.k('create ns n1')
    broker.connect('outside')
    cls.create_basic_dep()
    test = broker.coreV1.list_namespaced_service(namespace='default')
    print(f"OR NAH {test}")

    # cls.create_basic_dep()

  @classmethod
  def tearDownClass(cls):
    cls.k('delete ns n1')
    cls.k('delete clusterrolebinding nectar')

  def test_name(self):
    # kat_dep = KatDep(self.read_dep('d1'))
    # self.assertEqual(kat_dep.name, 'd1')
    pass


me = TestKatDep
