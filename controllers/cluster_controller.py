#!/usr/bin/env python3
from flask import Blueprint

from helpers.kube_broker import broker
from helpers.cluster_helper import ClusterHelper
from helpers.res_utils import ResUtils
from stunt_pods.stunt_pod import StuntPod

controller = Blueprint('cluster_controller', __name__)

@controller.route('/api/cluster/namespaces')
def namespaces():
  broker.check_connected()
  _namespaces = ClusterHelper.list_namespaces()
  return {"data": _namespaces}

@controller.route('/api/cluster/label_combinations')
def label_combinations():
  broker.check_connected()
  combinations = ClusterHelper.label_combinations()
  return {"data": list(set(combinations))}

@controller.route('/api/cluster/stunt_pods')
def stunt_pods():
  broker.check_connected()
  ser = [ResUtils.full_ser(pod) for pod in StuntPod.stunt_pods()]
  return {"data": ser}

@controller.route('/api/cluster/kill_stunt_pods', methods=['POST'])
def kill_stunt_pods():
  StuntPod.kill_stunt_pods()
  return {"data": "done"}
