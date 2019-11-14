from typing import List

from kubernetes.client import V1Service

from k8_kat.dep.dep_collection import DepCollection
from k8_kat.dep.kat_dep import KatDep
from k8_kat.svc.svc_query_exec import SvcQueryExec as Svc


class DepComposer:

  @staticmethod
  def svcs_for_dep_coll(dep_coll: DepCollection) -> List[V1Service]:
    if dep_coll.query.is_single_ns():
      return Svc.fetch_for_single_ns(dep_coll.query.namespace, None)
    else:
      return Svc.fetch_for_all_ns(None)

  @staticmethod
  def pods_for_dep_coll(dep_coll: DepCollection) -> List[V1Service]:
    if dep_coll.query.is_single_ns():
      return Svc.fetch_for_single_ns(dep_coll.query.namespace, None)
    else:
      return Svc.fetch_for_all_ns(None)

  @staticmethod
  def associate_svcs(dep_coll: DepCollection) -> [KatDep]:
    raw_svcs = me.svcs_for_dep_coll(dep_coll)
    me.assoc_all(dep_coll, raw_svcs, 'svcs')

  @staticmethod
  def associate_pods(dep_coll: DepCollection) -> [KatDep]:
    raw_svcs = me.svcs_for_dep_coll(dep_coll)
    me.assoc_all(dep_coll, raw_svcs, 'svcs')

  @staticmethod
  def assoc_all(dep_coll: DepCollection, others: List[V1Service], method: str):
    for dep in dep_coll.go():
      getattr(dep, f"assoc_{method}")(others)


me = DepComposer
