import os
import unittest
from typing import Tuple, List

from helpers.dep_helper import DepHelper as SafeDep

from helpers.kube_broker import broker
from utils.utils import Utils

NAMESPACES = ['n1', 'n2']

class K8katTest(unittest.TestCase):

  @staticmethod
  def k(cmd: str):
    os.system(f"microk8s.kubectl {cmd}")

  @staticmethod
  def nk(cmd: str, ns: str):
    if ns:
      me.k(f"{cmd} -n {ns}")
    else:
      me.k(cmd)

  @staticmethod
  def read_dep(ns, name):
    return SafeDep.find(ns, name)

  @staticmethod
  def nk_create_dep(ns: str, dep_name: str, labels=None):
    me.nk(f"create deploy {dep_name} --image nginx", ns)
    if labels:
      me.nk_label_dep(ns, dep_name, labels)

  @staticmethod
  def nk_apply(ns, fname):
    import app
    root = app.app.instance_path.replace('/instance', '')
    filename = os.path.join(root, f"tests/yamls/{fname}.yaml")
    me.nk(f"apply -f {filename}", ns)

  @staticmethod
  def k_apply(fname):
    me.nk_apply(None, fname)

  @staticmethod
  def nk_label_dep(ns: str, dep_name: str, labels: List[Tuple[str, str]]):
    lb_str = ' '.join([f"{l[0]}={l[1]}" for l in labels])
    me.nk(f"label deploy {dep_name} {lb_str}", ns)

  @staticmethod
  def prepare_cluster():
    if Utils.is_ci():
      me.k_apply('ci-perms')

  @classmethod
  def setUpClass(cls) -> None:
    cls.prepare_cluster()
    broker.connect('outside')

    if Utils.is_ci():
      for ns in NAMESPACES:
        cls.k(f"create ns {ns}")

  @classmethod
  def tearDownClass(cls):
    if Utils.is_ci() and not Utils.is_ci_keep():
      cls.k('delete clusterrolebinding nectar')
      for ns in NAMESPACES:
        cls.k(f"delete ns {ns}")
    else:
      for ns in NAMESPACES:
        cls.nk("delete deploy --all", ns)


me = K8katTest
