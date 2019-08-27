#!/usr/bin/env python3

from kube_broker import broker
from pod_helper import PodHelper
from svc_helper import SvcHelper
from utils import Utils

class DepHelper:
  @staticmethod
  def find(namespace, name):
    return broker.appsV1Api.read_namespaced_deployment(
      namespace=namespace,
      name=name
    )

  @staticmethod
  def ns_whitelist(whitelist, deps):
    disc = lambda d: d.metadata.namespace in whitelist
    return list(filter(disc, deps))

  @staticmethod
  def ns_blacklist(blacklist, deps):
    disc = lambda d: d.metadata.namespace not in blacklist
    return list(filter(disc, deps))

  @staticmethod
  def ns_filter(deps, filters, _type='whitelist'):
    method = DepHelper.ns_whitelist if _type == 'whitelist' else DepHelper.ns_blacklist
    return method(filters, deps)

  @staticmethod
  def label_whitelist(whitelist, deps):
    lm = lambda d: d.spec.selector.match_labels.items() <= whitelist.items()
    return list(filter(lm, deps))

  @staticmethod
  def label_blacklist(whitelist, deps):
    lm = lambda d: not d.spec.selector.match_labels.items() <= whitelist.items()
    return list(filter(lm, deps))

  @staticmethod
  def lb_filter(filters, _type='whitelist', deps=None):
    if deps is None:
      deps = broker.appsV1Api.list_deployment_for_all_namespaces().items
    method = DepHelper.label_whitelist if _type == 'whitelist' else DepHelper.label_blacklist
    return method(filters, deps)

  @staticmethod
  def ns_lb_filter(ns_filters, ns_filter_type, lb_filters, lb_filter_type):
    deps = broker.appsV1Api.list_deployment_for_all_namespaces().items
    return DepHelper.ns_filter(deps, ns_filters, ns_filter_type)
    # return DepHelper.lb_filter(deps, lb_filters, lb_filter_type)

  @staticmethod
  def easy():
    return broker.appsV1Api.list_namespaced_deployment(namespace='default').items

  @staticmethod
  def full_list(deps):
    all_pods = broker.coreV1.list_pod_for_all_namespaces().items
    all_svc = broker.coreV1.list_service_for_all_namespaces().items
    assoc_er = lambda d: DepHelper.assoc_deps_pods_svc(d, all_pods, all_svc)
    assoc_ed = list(map(assoc_er, deps))
    return list(map(DepHelper.complex_ser, assoc_ed))

  @staticmethod
  def assoc_deps_pods_svc(dep, all_pods, all_svcs):
    assoc_pods = PodHelper.pods_for_dep(dep.metadata.name, all_pods)
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
      "std_container_count": len(containers) == 1,
      "image_name": Utils.try_or(lambda: containers[0].image),
      "image_pull_policy": Utils.try_or(lambda: containers[0].image_pull_policy)
    }

  # noinspection PyTypeChecker
  @staticmethod
  def complex_ser(bundle):
    base = DepHelper.simple_ser(bundle['dep'])
    child_nodes = {
      'pods': list(map(PodHelper.child_ser, bundle['pods'])),
      'services': list(map(SvcHelper.child_ser, bundle['svcs'])),
    }
    return dict(list(base.items()) + list(child_nodes.items()))
