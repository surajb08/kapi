from analysis_suites.network.network_suite import NetworkSuiteStep

class ServiceVisibleStep(NetworkSuiteStep):

  def has_one_ref(self, line):
    pass

  def perform(self):
    fqdn = f"{self.svc_name}.{self.ns}"
    command = f"nslookup {fqdn}"
    output = self.stunt_pod.execute_command(command)
    lines = output.split("\n")


    output = self.stunt_pod
    if output['finished']:
      super().as_positive(
        outputs=lines,
        bundle={**output}
      )
    else:
      super().as_negative(
        outputs=["Could not connect"],
        bundle={**output}
      )
