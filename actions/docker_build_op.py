import time


from actions.docker_op import DockerOp

class DockerBuildOp(DockerOp):

  def __init__(self, zip_url, df_path, out_name):
    super().__init__(None)
    self.zip_url = zip_url
    self.out_name = out_name
    self.df_path = df_path

  def _command(self):
    cmd = f"docker build {self.zip_url} -t {self.out_name} -f {self.df_path}"
    print(cmd)
    return cmd

  @staticmethod
  def play():
    worker = DockerBuildOp('.', '/Dockerfile', 'testy')

    print(f"Job name: {worker.job_name}")
    print(f"Daemon Host: {worker.daemon_host()}")

    worker.create_and_run_job()

  @staticmethod
  def play2():
    df = "robonectar-moderator_cms-47ccb675c4b8678609cbce5d12926bdd2e83030f/Dockerfile"
    _zip = "https://storage.googleapis.com/nectar-mosaic-public/dummy-tar.tar.gz"
    worker = DockerBuildOp(_zip, df, 'whatever')
    worker.create_and_run_job()

    ch = None
    while ch is not 'x':
      ch = input()
      print(worker.logs())
