from analysis_suites.network.network_suite import NetworkSuiteStep

class DoesSvcConnectStep(NetworkSuiteStep):

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

  @staticmethod
  def test():
    worker = DoesSvcConnectStep(
      from_port="80",
      svc_name="moderator",
      dep_name="moderator",
      dep_ns="default"
    )

    worker.perform()

    return worker
