#!/usr/bin/env python3
from flask import Blueprint, request

from actions.annotator import Annotator
from helpers.dep_helper import DepHelper
from helpers.res_utils import ResUtils
from k8_kat.dep.dep_serializers import DepSerialization as Ser
from utils.utils import Utils
from k8_kat.base.k8_kat import K8kat

controller = Blueprint('deployments_controller', __name__)


@controller.route('/api/deployments/across_namespaces')
def across_namespaces():
  return dict(data=ResUtils.dep_by_ns())

@controller.route('/api/deployments/filtered')
def filtered():
  result = list(map(DepHelper.simple_ser, params_to_deps()))
  return {"data": result}

@controller.route('/api/deployments/<ns>/<name>')
def show(ns, name):
  deployment = K8kat.deps(in_ns=ns).find(name).with_friends()
  return dict(data=deployment.serialize(Ser.with_pods_and_svcs))

@controller.route('/api/deployments')
def index():
  filtered_deployments = params_to_deps()

  if request.args.get('full') == 'true':
    payload = DepHelper.full_list(filtered_deployments)
  else:
    payload = list(map(DepHelper.simple_ser, params_to_deps()))
  return { 'data': payload }

@controller.route('/api/deployments/<namespace>/<name>/pods')
def list_pods(namespace, name):
  deployment = DepHelper.find(namespace, name)
  pods = ResUtils.pods_for_dep(deployment)
  serialized = list(map(ResUtils.full_ser, pods))
  return { 'data': serialized }

@controller.route('/api/deployments/<namespace>/<name>/annotate_git', methods=['POST'])
def annotate(namespace, name):
  annotator = Annotator(
    namespace=namespace,
    name=name,
    **request.json
  )
  annotations = annotator.annotate()
  return {"annotations": annotations}


def params_to_deps():
  ns_filters = request.args.get('ns_filters', '').split(',')
  ns_filter_type = request.args.get('ns_filter_type', 'whitelist')
  lb_filters = Utils.parse_dict_array(request.args.get('lb_filters', ''))
  lb_filter_type = request.args.get('lb_filter_type', 'blacklist')

  query = K8kat.deps().for_ns(ns_filter_type, ns_filters)
  query = query.for_lbs(lb_filter_type, lb_filters)
  result = query.go()

  return [dep.raw for dep in result]

