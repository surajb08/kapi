from analysis_suites.network.terminals import terminals
from analysis_suites.network.network_suite import BaseNetworkStep

class NoProblemStep(BaseNetworkStep):

  def _terminal_copy_bundle(self):
    return {}

  def load_copy_tree(self):
    print(f"Hey I'm returning everything! {terminals}")
    return terminals
