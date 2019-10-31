import time


from actions.docker_op import DockerOp

TAR_NAME = "repo-tar.tar.gz"
WORK_DIR = "cloned-repo"

class DockerBuildOp(DockerOp):

  def __init__(self, repo_tar_url, dockerfile_path, output_img):
    super().__init__(None)
    self.repo_tar_url = repo_tar_url
    self.output_img = output_img
    self.dockerfile_path = dockerfile_path

  def build_context(self):
    relative_path = self.dockerfile_path.replace("/Dockerfile", "")
    return f"{WORK_DIR}/.{relative_path}"

  def command(self):
    return f"wget -O {TAR_NAME} {self.repo_tar_url} -q && " \
           f"mkdir {WORK_DIR} && " \
           f"tar xzf {TAR_NAME} -C {WORK_DIR} --strip-components=1 && " \
           f"docker build {self.build_context()} -t {self.output_img} " \

  @staticmethod
  def play2():
    df = "/Dockerfile"
    _zip = "https://storage.googleapis.com/nectar-mosaic-public/news_crawler.tar.gz"
    worker = DockerBuildOp(_zip, df, 'xnectar/web-app:latest')
    worker.create_work_pod()
    worker.debug()
