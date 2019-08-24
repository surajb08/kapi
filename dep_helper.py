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
  def ns_whitelist(whitelist, deps = None):
    disc = lambda d: d.metadata.namespace in whitelist
    return list(filter(disc, deps))

  @staticmethod
  def ns_blacklist(blacklist, deps = None):
    disc = lambda d: d.metadata.namespace not in blacklist
    return list(filter(disc, deps))

  @staticmethod
  def ns_filter(filters, _type='whitelist'):
    deps = broker.appsV1Api.list_deployment_for_all_namespaces().items
    # print(deps)
    method = DepHelper.ns_whitelist if _type == 'whitelist' else DepHelper.ns_blacklist
    return method(filters, deps)

# broker.connect()
# res = DepHelper.ns_filter(['kube-system', None], "blacklist")
# print(res)
# print(len(res))