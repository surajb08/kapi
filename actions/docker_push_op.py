from actions.docker_op import DockerOp

class DockerPushOp(DockerOp):

  def __init__(self, username, password, out_name):
    super().__init__(None)
    self.username = username
    self.password = password
    self.out_name = out_name

  def _command(self):
    return f"docker push {self.out_name}"

  def run(self):
    pass

  @staticmethod
  def play():
    worker = DockerPushOp('xnectar', 'Kristn@bl00t', None)
    print(f"Job name: {worker.job_name}")
    print(f"Daemon Host: {worker.daemon_host}")
    worker.create_work_pod()

