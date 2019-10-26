from kubernetes.client import V1Job, V1ObjectMeta, V1JobSpec, V1PodTemplateSpec, V1PodSpec, V1Container

from helpers.kube_broker import broker


class DockerOps:

  def __init__(self, **args):
    self.namespace= args['namespace']
    self.df_path = args['df_path']
    self.url = args['url']
    self.output_name = args['output_name']


  @property
  def gen_command(self):
    return f"docker build -t {self.output_name} -f {self.df_path} {self.url}"

  def create_job(self):
    broker.batchV1.create_namespaced_job(
      namespace=self.namespace,
      body=V1Job(
        metadata=V1ObjectMeta(
          namespace=self.namespace,
          name="asd"
        ),
        spec=V1JobSpec(
          template=V1PodTemplateSpec(
            spec=V1PodSpec(
              containers=[
                V1Container(
                  image='docker'
                ),
                V1Container(
                  image='docker:18.05-dind'
                )
              ]
            )
          )
        )
      )
    )
