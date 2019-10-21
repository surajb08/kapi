from analysis_suites.network.network_suite import NetworkSuiteStep

class ServiceVisibleStep(NetworkSuiteStep):

  def has_required_ref(self, lines):
    per_line = lambda l: self.svc_name in l
    fqdn_lines = list(filter(per_line, lines))
    return len(fqdn_lines) > 0

  def perform(self):
    command = f"nslookup {self.fqdn}"
    output = self.stunt_pod.execute_command(command)
    lines = output.split("\n")

    return super().record_step_performed(
      outcome=self.has_required_ref(lines),
      outputs=lines,
      bundle={**output}
    )

