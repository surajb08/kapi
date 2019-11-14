import os
import unittest
from typing import Tuple

from helpers.dep_helper import DepHelper as SafeDep
from helpers.kube_broker import broker


class K8katTest(unittest.TestCase):

  @staticmethod
  def k(cmd: str):
    os.system(f"microk8s.kubectl {cmd}")

  @staticmethod
  def nk(cmd: str, ns: str = 'n1'):
    me.k(f"{cmd} -n {ns}")

  @staticmethod
  def read_dep(ns, name):
    return SafeDep.find(ns, name)

  @staticmethod
  def nk_create_dep(dep_name: str, ns):
    me.nk(f"create deploy {dep_name} --image nginx", ns)

  @staticmethod
  def nk_label_dep(ns: str, dep_name: str, label: Tuple[str, str]):
    me.nk(f"label deploy {dep_name} {label[0]}={label[1]}", ns)

  @staticmethod
  def create_basic_dep():
    me.nk_create_dep('d1', 'n1')
    me.nk_label_dep('n1', 'd1', ('l1', 'v1'))

  @staticmethod
  def prepare_cluster():
    import app
    # filename = os.path.join(app.app.instance_path, 'ci-perms.yaml')
    # filename = filename.replace('/instance', '')
    # cls.k(f"apply -f {filename}")
    # cls.k('create ns n1')
    pass

  @classmethod
  def setUpClass(cls) -> None:
    cls.prepare_cluster()
    broker.connect('outside')
    # cls.create_basic_dep()

  @classmethod
  def tearDownClass(cls):
    # cls.k('delete ns n1')
    # cls.k('delete clusterrolebinding nectar')
    cls.nk('delete deploy --all', 'n1')
    pass

me = K8katTest