#!/usr/bin/env python3
from flask import Blueprint

from helpers.kube_broker import broker
from helpers.cluster_helper import ClusterHelper

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
  return {"data": combinations}
