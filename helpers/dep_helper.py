#!/usr/bin/env python3

from helpers.kube_broker import broker
from helpers.res_utils import ResUtils
from helpers.svc_helper import SvcHelper
from utils.utils import Utils

class DepHelper:
  @staticmethod
  def find(namespace, name):
    return broker.appsV1Api.read_namespaced_deployment(
      namespace=namespace,
      name=name
    )

  @staticmethod
  def full_list(deps):
    all_pods = broker.coreV1.list_pod_for_all_namespaces().items
    all_svc = broker.coreV1.list_service_for_all_namespaces().items
    bundler = lambda d: DepHelper.assoc_deps_pods_svc(d, all_pods, all_svc)
    bundles = list(map(bundler, deps))
    return list(map(DepHelper.complex_ser, bundles))

  @staticmethod
  def full_single(dep):
    all_pods = broker.coreV1.list_pod_for_all_namespaces().items
    all_svc = broker.coreV1.list_service_for_all_namespaces().items
    bundle = DepHelper.assoc_deps_pods_svc(dep, all_pods, all_svc)
    return DepHelper.complex_ser(bundle)

  @staticmethod
  def restart_nectar_pods(dep_name):
    dep = DepHelper.find('nectar', dep_name)
    pod_labels = dep.spec.template.metadata.labels
    selector = Utils.dict_to_eq_str(pod_labels)
    broker.coreV1.delete_collection_namespaced_pod(
      'nectar',
      label_selector=selector
    )

  @staticmethod
  def assoc_deps_pods_svc(dep, all_pods, all_svcs):
    assoc_pods = ResUtils.pods_for_dep_loaded(dep.metadata.name, all_pods)
    assoc_svc = SvcHelper.svcs_for_dep(dep, all_svcs)
    return {
      "dep": dep,
      "pods": assoc_pods,
      "svcs": assoc_svc
    }

  @staticmethod
  def simple_ser(dep):
    containers = dep.spec.template.spec.containers

    return {
      "name": dep.metadata.name,
      "namespace": dep.metadata.namespace,
      "labels": dep.spec.selector.match_labels,
      "replicas": dep.spec.replicas,
      "image_name": Utils.try_or(lambda: containers[0].image),
      "container_name": Utils.try_or(lambda: containers[0].name),
      "image_pull_policy": Utils.try_or(lambda: containers[0].image_pull_policy),
      "commit": DepHelper.commit_ser(dep)
    }

  @staticmethod
  def commit_ser(dep):
    bundle = {
      "sha": dep.metadata.annotations.get('commit-sha'),
      "branch": dep.metadata.annotations.get('commit-branch'),
      "message": dep.metadata.annotations.get('commit-message'),
      "timestamp": dep.metadata.annotations.get('commit-timestamp')
    }
    is_worthwhile = bundle['sha'] or bundle['message']
    return bundle if is_worthwhile else None

  # noinspection PyTypeChecker
  @staticmethod
  def complex_ser(bundle):
    base = DepHelper.simple_ser(bundle['dep'])
    child_nodes = {
      'pods': list(map(ResUtils.child_ser, bundle['pods'])),
      'services': list(map(SvcHelper.child_ser, bundle['svcs'])),
    }
    return dict(list(base.items()) + list(child_nodes.items()))
