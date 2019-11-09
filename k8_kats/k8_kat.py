from k8_kats.dep_collection import DepCollection


class K8Kat:

  @staticmethod
  def deps(**kwargs):
    query = DepCollection()
    return query.where(**kwargs)
