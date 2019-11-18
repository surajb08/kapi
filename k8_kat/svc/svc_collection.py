from k8_kat.base.res_collection import ResCollection
from k8_kat.base.res_query import ResQuery
from k8_kat.svc.kat_svc import KatSvc
from k8_kat.svc.svc_query_exec import SvcQueryExec

class SvcCollection(ResCollection):
  def create_query(self):
    return ResQuery(SvcQueryExec(), KatSvc)


