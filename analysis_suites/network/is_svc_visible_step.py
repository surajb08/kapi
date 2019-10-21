from analysis_suites.network.network_suite import NetworkSuiteStep

class IsSvcVisibleStep(NetworkSuiteStep):

  def has_required_ref(self, lines):
    per_line = lambda line: (self.svc_name in line)
    fqdn_lines = list(filter(per_line, lines))
    return len(fqdn_lines) > 0

  def perform(self):
    command = f"nslookup {self.fqdn}"
    output = self.stunt_pod.execute_command(command)
    lines = list(map(lambda l: l.strip(), output.split("\n")))
    lines = list(filter(lambda l: l, lines))

    return super().record_step_performed(
      outcome=self.has_required_ref(lines),
      outputs=lines,
      bundle={}
    )

