#!/usr/bin/env python3
import time

from kubernetes.client import V1Scale, V1ScaleSpec

from dep_helper import DepHelper
from kube_broker import broker
from pod_helper import PodHelper


class ImageReloader:

  def __init__(self, dp_namespace, dp_name, mode, scale_to=None):
    self.deployment = DepHelper.find(dp_namespace, dp_name)
    self.mode = mode
    self.scale_to = self.decide_scale_target(scale_to)
    self.init_pod_names = self.load_pod_names()

  def decide_scale_target(self, scale_to):
    if self.mode == 'scale':
      return scale_to
    else:
      return self.deployment.spec.replicas

  def load_pod_names(self):
    work = lambda p: p.metadata.name
    pods = PodHelper.pods_for_dep(self.deployment)
    return list(map(work, pods))

  def await_old_pods_dead(self):
    max_tries = len(self.init_pod_names) * 5
    all_dead = False
    for attempt in range(0, max_tries):
      crt_pod_names = self.load_pod_names()
      overlap = set(self.init_pod_names).intersection(crt_pod_names)
      print(f"Attempt {attempt} overlap({len(overlap)}): {overlap}")
      all_dead = len(overlap) == 0
      if all_dead: break;
      time.sleep(3)

    return all_dead

  def run(self):
    if self.mode == 'reload':
      print(f"SCALING DOWN FIRST {self.mode}")
      self.scale(0)
      print(f"Scaling to final {self.scale_to}")
    self.scale(self.scale_to)

  def scale(self, replicas):
    broker.appsV1Api.patch_namespaced_deployment_scale(
      name=self.deployment.metadata.name,
      namespace=self.deployment.metadata.namespace,
      body=V1Scale(
        spec=	V1ScaleSpec(
          replicas=replicas
        )
      )
    )

  @staticmethod
  def play():
    reloader = ImageReloader('default', 'ruby-cluster', "scale", 0)
    print(f"Initial pods: {reloader.init_pod_names}")
    print(f"Desired replicas: {reloader.scale_to}")
    reloader.run()
    return reloader
