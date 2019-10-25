from analysis_suites.network import terminals
from analysis_suites.network.network_suite import BaseNetworkStep

class PortsConnectingStep(BaseNetworkStep):

  def _terminal_copy_bundle(self):
    return {}

  def load_copy_tree(self):
    return terminals
