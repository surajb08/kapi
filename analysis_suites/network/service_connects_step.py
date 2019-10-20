from analysis_suites.network.network_suite import NetworkSuiteStep

class ServiceConnectsStep(NetworkSuiteStep):

  def perform(self):
    worker = self.stunt_pod

    worker.exec_command

    return ""

  @staticmethod
  def test():
    worker = ServiceConnectsStep(
      from_port="80",
      svc_name="moderator",
      dep_name="moderator",
      dep_ns="default"
    )

    return worker
