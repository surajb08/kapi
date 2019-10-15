class Reporter:
  def report(self, outcome, message):
    return {
      "outcome": outcome,
      "message": message
    }

class PortParityReporter(Reporter):
  def __init__(self, svc_name, out_port, df_port):
    self.svc_name = svc_name
    self.out_port = out_port
    self.df_port = df_port

  def ports_match(self):
    return self.report(
      False,
      f"{self.svc_name}'s open port[{self.out_port}] correctly maps "
      f"to port[{self.df_port}] from your Dockerfile",
    )

  def ports_dont_match(self):
    return self.report(
      True,
      f"{self.svc_name}'s open port[{self.out_port}] is not mapping "
      f"to port[{self.df_port}] from your Dockerfile"
    )

  def dockerfile_shy(self):
    return self.report(
      None,
      f"Your Dockerfile isn't exposing ports {self.out_port}"
      f" Unless it's exposed in the base image, this is the problem."
    )


class ServiceTypeReporter(Reporter):
  def __init__(self, _type):
    self._type = _type

  def in_ns_all_good(self):
    return self.report(
      False,
      f"A {self._type} can handle in-namespace traffic, "
      f"so that's no the problem"
    )

  def out_cluster_correct(self):
    return self.report(
      False,
      f"You're using a {self._type}, so that's not the problem"
    )

  def out_cluster_mismatch(self):
    return self.report(
      True,
      f"{self._type}'s can't handle outside traffic. This is the problem."
    )

class PodsRunningReporter(Reporter):
  def __init__(self, dep_name, running):
    self.dep_name = dep_name
    self.running = running

  def some_running(self):
    return self.report(
      False,
      f"{self.dep_name} has {self.running} running pods, "
      f"so that's not the problem."
    )

  def none_running(self):
    return self.report(
      True,
      f"{self.dep_name()} has no running pods. That's a blocker."
    )

class PortTypeReporter(Reporter):
  def __init__(self, svc_name, port):
    self.svc_name = svc_name
    self.port = port

  def port_is_int(self):
    return self.report(
      False,
      f"{self.svc_name}'s target_port {self.port} "
      f"is an integer, as it should be."
    )

  def port_is_string(self):
    return self.report(
      None,
      f"{self.svc_name}'s target_port {self.port} "
      f"is a string but should be an integer"
    )