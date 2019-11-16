#!/usr/bin/env python3

from flask import Blueprint, request, jsonify

from actions.annotator import Annotator
from helpers.res_utils import ResUtils
from k8_kat.base.k8_kat import K8kat
from k8_kat.dep.dep_composer import DepComposer
from k8_kat.dep.dep_serializers import DepSerialization as Ser
from k8_kat.pod.pod_serialization import PodSerialization

controller = Blueprint('deployments_controller', __name__)


@controller.route('/api/deployments')
def index():
  deps = params_to_deps()
  serialized = [Ser.as_needed(dep) for dep in deps]
  return jsonify(dict(data=serialized))

@controller.route('/api/deployments/<ns>/<name>')
def show(ns, name):
  dep = K8kat.deps().ns(ns).find(name).with_friends()
  serialized = dep.serialize(Ser.with_pods_and_svcs)
  return jsonify(serialized)

@controller.route('/api/deployments/across_namespaces')
def across_namespaces():
  return jsonify(dict(data=ResUtils.dep_by_ns()))

@controller.route('/api/deployments/<ns>/<name>/pods')
def deployment_pods(ns, name):
  dep = K8kat.deps().ns(ns).find(name)
  serialized = [PodSerialization.standard(pod) for pod in dep.pods()]
  return jsonify(dict(data=serialized))

@controller.route('/api/deployments/<ns>/<name>/annotate_git', methods=['POST'])
def annotate(ns, name):
  annotator = Annotator(
    namespace=ns,
    name=name,
    **request.json
  )
  annotations = annotator.annotate()
  return jsonify(dict(annotations=annotations))

def eq_strs_to_tups(as_str: str):
  return [tuple(eq.split(':')) for eq in as_str.split(',')]

def params_to_deps():
  q = K8kat.deps()

  ns_white = request.args.get('ns_filter_type', 'whitelist')
  ns_white = True if ns_white == 'whitelist' else False
  ns_filters = request.args.get('ns_filters')
  ns_filters = ns_filters and ns_filters.split(',') or None

  lb_white = request.args.get('lb_filter_type', 'blacklist')
  lb_white = True if lb_white == 'whitelist' else False
  lb_filters = request.args.get('lb_filters')
  lb_filters = lb_filters and eq_strs_to_tups(lb_filters)

  if ns_filters is not None:
    q = q.ns(ns_filters) if ns_white else q.not_ns(ns_filters)

  if lb_filters is not None:
    q = q.lbs_inc_each(lb_filters) if lb_white else q.lbs_exc_each(lb_filters)

  deps = q.go()

  if request.args.get('svcs') == 'true':
    DepComposer.associate_svcs(deps)

  if request.args.get('pods') == 'true':
    DepComposer.associate_pods(deps)

  return deps
