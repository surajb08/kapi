from analysis_suites.network.network_suite import BaseNetworkStep
from analysis_suites.network.terminals import terminals


class ContainerProblemStep(BaseNetworkStep):

  def _terminal_copy_bundle(self):
    return {}

  def load_copy_tree(self):
    return terminals
