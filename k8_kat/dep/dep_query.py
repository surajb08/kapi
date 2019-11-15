from k8_kat.base.res_query import ResQuery
from k8_kat.dep.dep_query_exec import DepQueryExec
from k8_kat.dep.kat_dep import KatDep


class DepQuery(ResQuery):
  def __init__(self):
    super().__init__(DepQueryExec(), KatDep)

