from helpers.dep_helper import DepHelper
from helpers.kube_broker import broker


class Annotator:
  def __init__(self, namespace, name, **kwargs):
    self.deployment = DepHelper.find(namespace, name)
    self.sha = kwargs['sha']
    self.message = kwargs['message']
    self.branch = kwargs['branch']
    self.author = kwargs['author']

  def gen_annotation_dict(self):
    return {
      "commit-sha": self.sha,
      "commit-message": self.message,
      "commit-branch": self.branch
    }

  def annotate(self):
    annotations = self.deployment.metadata.annotations
    updated_annot = { **annotations, **self.gen_annotation_dict() }
    self.deployment.metadata.annotations = updated_annot
    broker.appsV1Api.patch_namespaced_deployment(
      name=self.deployment.metadata.name,
      namespace=self.deployment.metadata.namespace,
      body=self.deployment
    )

  @staticmethod
  def play():
    params = {
      "sha": "sha",
      "message": "message",
      "branch": "branch",
      "author": "author"
    }

    inst = Annotator('default', 'moderator', **params)
    inst.annotate()