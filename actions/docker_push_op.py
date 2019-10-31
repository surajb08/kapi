from actions.docker_op import DockerOp

class DockerPushOp(DockerOp):

  def __init__(self, username, password, image_name):
    super().__init__(None)
    self.username = username
    self.password = password
    self.image_name = image_name

  def command(self):
    return f"echo {self.password} | docker login -u {self.username} --password-stdin && " \
           f"docker push {self.image_name}"

  def run(self):
    pass

  @staticmethod
  def play():
    worker = DockerPushOp('xnectar', 'Kristn@bl00t', "xnectar/web-app:latest")
    print(f"Job name: {worker.pod_name}")
    print(f"Daemon Host: {worker.daemon_host}")
    worker.create_work_pod()
    worker.debug()

