import time


from actions.docker_op import DockerOp

class DockerBuildOp(DockerOp):

  def __init__(self, zip_url, df_path, out_name):
    super().__init__(None)
    self.zip_url = zip_url
    self.out_name = out_name
    self.df_path = df_path

  def _command(self):
    return f"docker build {self.zip_url} -t {self.out_name} -f {self.df_path}"

  @staticmethod
  def play():
    worker = DockerBuildOp('.', '/Dockerfile', 'testy')

    print(f"Job name: {worker.pod_name}")
    print(f"Daemon Host: {worker.daemon_host()}")

    worker.create_work_pod()

  @staticmethod
  def play2():
    df = "robonectar-news_crawler-3d6bc9c204480dc05c43fface0e13c0049a4311c/Dockerfile"
    _zip = "https://storage.googleapis.com/nectar-mosaic-public/news_crawler.tar.gz"
    worker = DockerBuildOp(_zip, df, 'whatever')
    worker.create_work_pod()

    while not worker.is_pod_ready():
      print(f"Wait for pod birth...")
      time.sleep(1)

    while True:
      print(f"-------------------------STATUS {worker.status()}--------------------------")
      print(worker.logs())
      time.sleep(3)

