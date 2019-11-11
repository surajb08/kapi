from k8_kat.base.res_collection import ResCollection
from k8_kat.svc.svc_query import SvcQuery

class SvcCollection(ResCollection):
  def create_query(self):
    return SvcQuery()


