from helpers.res_utils import ResUtils
from k8_kat.rs.rs_outbound import RsOutbound

class PodDiplomat:

  @staticmethod
  def pod_dep(pod):
    rs = PodDiplomat.pod_rs(pod)
    return RsOutbound.rs_dep(rs) if rs else None

  @staticmethod
  def pod_rs(pod):
    refs = pod.metadata.owner_references
    rs_refs = [ref for ref in refs if ref.kind == 'ReplicaSet']
    if len(rs_refs) is 1:
      rs_name = rs_refs[0].name
      return ResUtils.find_rs(pod.metadata.namespace, rs_name)
    else:
      return None
