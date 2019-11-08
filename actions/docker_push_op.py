from actions.docker_op import DockerOp

class DockerPushOp(DockerOp):

  def __init__(self, username, password, image_name):
    super().__init__(None)
    self.username = username
    self.password = password
    self.image_name = image_name

  def command(self):
    return f"echo {self.password} | docker login -u {self.username} --password-stdin && " \
           f"echo \"yea it's 2019 maybe support token auth lol\" && " \
           f"docker push {self.image_name}"

  @staticmethod
  def play():
    DockerOp.purge()
    worker = DockerPushOp('xavierdevact', "dudeomgits2019", "xavierdevact/web-app:latest")
    worker.create_work_pod()
    worker.debug()