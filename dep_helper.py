#!/usr/bin/env python3

from kube_broker import broker

class DepHelper:
  @staticmethod
  def find(namespace, name):
    return broker.appsV1Api.read_namespaced_deployment(
      namespace=namespace,
      name=name
    )

  @staticmethod
  def services(deployment):
    match_labels = deployment.spec.selector.match_labels
    returned_services = broker.coreV1.list_service_for_all_namespaces()
    return list(filter(lambda x: x.spec.selector == match_labels, returned_services.items))

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
    deps = broker.appsV1Api.list_deployment_for_all_namespaces().items()
    deps = DepHelper.ns_filter(deps, ns_filters, ns_filter_type)
    return DepHelper.lb_filter(deps, lb_filters, lb_filter_type)

  @staticmethod
  def simple_ser(deployment):
    return {
      "name": deployment.metadata.name,
      "namespace": deployment.metadata.namespace,
      "labels": deployment.spec.selector.match_labels
    }