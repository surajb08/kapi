#!/usr/bin/env python3
from flask import Blueprint

from kube_broker import broker

controller = Blueprint('deployments_controller', __name__)


@controller.route('/api/deployments/across_namespaces')
def across_namespaces():
  broker.check_connected()
  dump = broker.appsV1Api.list_deployment_for_all_namespaces().items
  dump = list(filter(lambda d: d.metadata.namespace != 'kube-system', dump))
  min_dep = lambda d: {"name": d.metadata.name, "namespace": d.metadata.namespace}
  serialized = list(map(min_dep, dump))
  unique_names = set(map(lambda d: d['name'], serialized))

  output = []
  for name in unique_names:
    matching_deps = list(filter(lambda d: d['name'] == name, serialized))
    corresponding_namespaces = list(map(lambda d: d['namespace'], matching_deps))
    output.append({
      "name": name,
      "namespaces": corresponding_namespaces
    })

  return { "data": output }
