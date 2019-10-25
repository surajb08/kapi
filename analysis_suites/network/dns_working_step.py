from analysis_suites.network.terminals import terminals
from analysis_suites.network.network_suite import BaseNetworkStep

class DnsWorkingStep(BaseNetworkStep):

  def _terminal_copy_bundle(self):
    return {}

  def load_copy_tree(self):
    return terminals
