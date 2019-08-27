#!/usr/bin/env python3
from flask import Blueprint, request

from dep_helper import DepHelper
from kube_broker import broker
from utils import Utils

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

@controller.route('/api/deployments/filtered')
def filtered():

  print(request.args)

  ns_filter = request.args.get('ns_filters', default='').split(',')
  ns_filter_type = request.args.get('ns_filter_type')

  lb_filter = Utils.parse_dict(request.args.get('lb_filters', default=''))
  lb_filter_type = request.args.get('lb_filter_type')

  print(ns_filter)
  print(ns_filter_type)

  print(lb_filter)
  print(lb_filter_type)

  filtered_deps = DepHelper.ns_filter(ns_filter, ns_filter_type)
  # lb_filtered = DepHelper.label_filter(lb_filter, lb_filter_type, ns_filtered)
  #
  result = list(map(DepHelper.simple_ser, filtered_deps))

  return { "data": result }

