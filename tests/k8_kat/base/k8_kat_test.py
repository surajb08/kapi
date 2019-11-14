import os
import unittest
from typing import Tuple, List

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
  def nk_create_dep(ns: str, dep_name: str, labels=None):
    me.nk(f"create deploy {dep_name} --image nginx", ns)
    if labels:
      me.nk_label_dep(ns, dep_name, labels)

  @staticmethod
  def nk_label_dep(ns: str, dep_name: str, labels: List[Tuple[str, str]]):
    lb_str = ' '.join([f"{l[0]}={l[1]}" for l in labels])
    me.nk(f"label deploy {dep_name} {lb_str}", ns)

  @staticmethod
  def create_basic_dep():
    me.nk_create_dep('n1', 'd1')
    me.nk_label_dep('n1', 'd1', [('l1', 'v1')])

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
    pass


me = K8katTest
