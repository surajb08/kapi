
class DepSerialization:

  @staticmethod
  def simple(dep):
    return {
      "name": dep.name,
      "namespace": dep.namespace,
      "labels": dep.labels,
      "replicas": dep.raw.spec.replicas,
      "image_name": dep.image_name,
      "container_name": dep.container_name,
      "commit": dep.commit
    }
