#!/usr/bin/env python3

from helpers.dep_helper import DepHelper
from helpers.kube_broker import broker

class ImageChanger:

  def __init__(self, dp_namespace, dp_name, target_name):
    self.deployment = DepHelper.find(dp_namespace, dp_name)
    self.target_name = target_name

  def run(self):
    self.deployment.spec.template.spec.containers[0].image = self.target_name
    broker.appsV1Api.patch_namespaced_deployment(
      namespace=self.deployment.metadata.namespace,
      name=self.deployment.metadata.name,
      body=self.deployment
    )
    return True

  @staticmethod
  def play():
    inst = ImageChanger('default', 'ruby-cluster', 'xnectar/rube:latest')
    inst.run()