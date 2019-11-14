from typing import List

from kubernetes.client import V1Service

from helpers.kube_broker import broker
from k8_kat.dep.dep_collection import DepCollection
from k8_kat.dep.kat_dep import KatDep


class DepComposer:

  @staticmethod
  def svcs_for_dep_coll(dep_coll: DepCollection) -> List[V1Service]:
    api = broker.coreV1
    if dep_coll.query.is_single_ns():
      ns = dep_coll.query.namespace
      return api.list_namespaced_service(namespace=ns).items
    else:
      return api.list_service_for_all_namespaces()

  @staticmethod
  def associate_svcs(dep_coll: DepCollection) -> [KatDep]:
    raw_svcs = me.svcs_for_dep_coll(dep_coll)
    me.zip_deps_and_foreign(dep_coll, raw_svcs, 'svcs')

  @staticmethod
  def zip_deps_and_foreign(dep_coll: DepCollection, others: List[V1Service], method: str):
    for dep in dep_coll.go():
      getattr(dep, f"assoc_{method}")(others)


me = DepComposer
