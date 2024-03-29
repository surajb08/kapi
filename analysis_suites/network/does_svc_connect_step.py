from analysis_suites.network.network_suite import BaseNetworkStep

class DoesSvcConnectStep(BaseNetworkStep):

  def perform(self):
    output = self.stunt_pod.curl(url=super().target_url)
    if output['finished']:
      super().as_positive(
        outputs=[f"{output['status']}", output['body'][0:100]],
        bundle={**output}
      )
    else:
      super().as_negative(
        outputs=["Could not connect"],
        bundle={**output}
      )
