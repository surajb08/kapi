
class PodSerialization:
  @staticmethod
  def standard(pod):
    return {
      'name': pod.name,
      'namespace': pod.namespace,
      'state': pod.full_status,
      'ip': pod.ip,
      'updated_at': pod.updated_at,
      'image_name': pod.image,
    }
