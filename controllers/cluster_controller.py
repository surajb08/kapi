#!/usr/bin/env python3
from flask import Blueprint, jsonify, request

from helpers.kube_broker import broker
from helpers.res_utils import ResUtils
from k8_kat.base.k8_kat import K8kat
from k8_kat.pod.pod_serialization import PodSerialization
from stunt_pods.stunt_pod import StuntPod

controller = Blueprint('cluster_controller', __name__)

@controller.route('/api/cluster/namespaces')
def namespaces():
  broker.check_connected()
  _namespaces = ResUtils.list_namespaces()
  return jsonify(data=_namespaces)

@controller.route('/api/cluster/label_combinations')
def label_combinations():
  broker.check_connected()
  combinations = ResUtils.label_combinations()
  return jsonify(data=list(set(combinations)))

@controller.route('/api/cluster/stunt_pods')
def stunt_pods():
  broker.check_connected()
  garbage = K8kat.pods().lbs_inc_each(StuntPod.labels()).go()
  ser = garbage.serialize(PodSerialization.standard)
  return jsonify(data=ser)

@controller.route('/api/cluster/label_matrix')
def label_matrix():
  get = lambda *keys: [request.args.get(k) for k in keys]
  _type, ns, name = get('matcher_type', 'matcher_ns', 'matcher_name')
  collection = K8kat.deps() if _type == 'deployment' else K8kat.svcs()
  matcher = collection.ns(ns).find(name)
  result = ResUtils.label_matrix(matcher)
  return jsonify(result)

@controller.route('/api/cluster/kill_stunt_pods', methods=['POST'])
def kill_stunt_pods():
  garbage = K8kat.pods().lbs_inc_each(StuntPod.labels())
  garbage.delete_all()
  return jsonify(status='done')
