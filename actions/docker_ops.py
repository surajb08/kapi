from kubernetes.client import V1Job, V1ObjectMeta, V1JobSpec, V1PodTemplateSpec, V1PodSpec, V1Container, V1EnvVar

from helpers.kube_broker import broker
from helpers.pod_helper import PodHelper
from utils.utils import Utils

class DockerOps:

  def __init__(self, **args):
    self.df_path = args['df_path']
    self.url = args['url']
    self.output_name = args['output_name']
    self.job_name = f"docker-build-push-{Utils.rand_str(4)}"
    self.daemon_host = self.find_daemon_host()

  def gen_command(self):
    flat = f"docker image ls"
    return flat.split(" ")

  def cleanup(self):
    broker.batchV1.delete_namespaced_job(
      namespace='nectar',
      name=self.job_name
    )

  def create_job(self):
    broker.batchV1.create_namespaced_job(
      namespace='nectar',
      body=V1Job(
        metadata=V1ObjectMeta(
          name=self.job_name
        ),
        spec=V1JobSpec(
          template=V1PodTemplateSpec(
            spec=V1PodSpec(
              restart_policy='Never',
              containers=[
                V1Container(
                  name='docker',
                  image='docker:latest',
                  command=self.gen_command(),
                  env=[
                    V1EnvVar(
                      name='DOCKER_HOST',
                      value=self.daemon_host
                    )
                  ]
                )
              ]
            )
          )
        )
      )
    )

  @staticmethod
  def find_daemon_host():
    labels = {'app': 'kapi'}
    kapi_pods = PodHelper.find_by_label('nectar', labels)
    return f"tcp://{kapi_pods[0].status.pod_ip}:2375"

  @staticmethod
  def play():
    worker = DockerOps(
      df_path='/Dockerfile',
      url='none',
      output_name='hey',
    )

    print(f"Job name: {worker.job_name}")
    print(f"Daemon Host: {worker.daemon_host}")

    worker.create_job()
