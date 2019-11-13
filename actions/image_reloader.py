#!/usr/bin/env python3
import time

from kubernetes.client import V1Scale, V1ScaleSpec

from helpers.dep_helper import DepHelper
from helpers.kube_broker import broker
from helpers.res_utils import ResUtils


class ImageReloader:

  def __init__(self, **args):
    self.deployment = args.get('deployment', self.find_dep(args))
    self.mode = args['mode']
    self.scale_to = self.decide_scale_target(args.get('scale_to', None))
    self.init_pod_names = self.load_pod_names()

  @staticmethod
  def find_dep(args):
    return DepHelper.find(args['dp_namespace'], args['dp_name'])

  def decide_scale_target(self, scale_to):
    if self.mode == 'scale':
      return scale_to
    else:
      return self.deployment.spec.replicas

  def load_pod_names(self):
    work = lambda p: p.metadata.name
    pods = ResUtils.pods_for_dep(self.deployment)
    return list(map(work, pods))

  def run(self):
    if self.mode == 'reload':
      self.scale(0)
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