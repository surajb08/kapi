from kubernetes.client import V1Deployment


class DepWarnings:

  @staticmethod
  def check_pods_in_same_ns(dep: V1Deployment):
    dep_ns = dep.metadata.namespace
    pods_ns = dep.spec.template.metadata.namespace
    if dep_ns != pods_ns:
      return {
        'name': "Deployment templating pods in different namespace",
        'detail': f"{dep_ns} != {pods_ns}"
      }