from k8_kat.base.res_query import ResQuery
from k8_kat.svc.kat_svc import KatSvc
from k8_kat.svc.svc_query_exec import SvcQueryExec


class SvcQuery(ResQuery):
  def __init__(self):
    super().__init__(SvcQueryExec(), KatSvc)
