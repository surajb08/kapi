from actions.docker_op import DockerOp

class DockerBuildOp(DockerOp):

  def __init__(self, zip_url, df_path, out_name):
    super().__init__(None)
    self.out_name = out_name or ''
    self.zip_url = zip_url
    self.df_path = df_path

  def _command(self):
    return f"docker build {self.zip_url} -f {self.df_path}"

  def run(self):
    pass

  @staticmethod
  def play():
    worker = DockerBuildOp('.', '/Dockerfile', 'testy')

    print(f"Job name: {worker.job_name}")
    print(f"Daemon Host: {worker.daemon_host}")

    worker.create_and_run_job()
