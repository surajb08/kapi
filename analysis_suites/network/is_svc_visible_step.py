from analysis_suites.network.network_suite import BaseNetworkStep

class IsSvcVisibleStep(BaseNetworkStep):

  def has_required_ref(self, lines):
    per_line = lambda line: (self.svc.name in line)
    fqdn_lines = list(filter(per_line, lines))
    return len(fqdn_lines) > 0

  def perform(self):
    command = f"nslookup {self.svc.short_dns}"
    output = self.stunt_pod.run(command)
    lines = list(map(lambda l: l.strip(), output.split("\n")))
    lines = list(filter(lambda l: l, lines))

    return super().record_step_performed(
      outcome=self.has_required_ref(lines),
      outputs=lines,
      bundle={}
    )

