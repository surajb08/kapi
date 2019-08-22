#!/usr/bin/env python3

from kube_broker import broker

class DepHelper:
  @staticmethod
  def find(namespace, name):
    return broker.appsV1Api.read_namespaced_deployment(
      namespace=namespace,
      name=name,
    )

  @staticmethod
  def services(deployment):
    match_labels = deployment.spec.selector.match_labels
    returned_services = broker.coreV1.list_service_for_all_namespaces()
    return list(filter(lambda x: x.spec.selector == match_labels, returned_services.items))
