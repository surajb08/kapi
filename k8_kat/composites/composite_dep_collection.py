from k8_kat.base.kat_res import KatRes
from k8_kat.base.res_collection import ResCollection
from k8_kat.dep.dep_collection import DepCollection
from k8_kat.dep.kat_dep import KatDep
from k8_kat.svc.svc_collection import SvcCollection


class CompositeDepCollection:

  @staticmethod
  def svcs_for_dep_col(dep_col: DepCollection) -> SvcCollection:
    pass

  @staticmethod
  def deps_with(dep_col: DepCollection, others: [str]) -> [KatDep]:
    if 'svcs' in others:
      svc_col = CompositeDepCollection.svcs_for_dep_col(dep_col)
      CompositeDepCollection.assoc_all(dep_col, svc_col, 'svcs')

  @staticmethod
  def assoc_all(dep_col: DepCollection, others: ResCollection, method: str):
    for dep in dep_col.go():
      getattr(dep, f"assoc_{method}")(others.go())






