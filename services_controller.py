#!/usr/bin/env python3
from flask import Blueprint

from kube_broker import broker
from dep_helper import DepHelper
from utils import Utils

controller = Blueprint('services_controller', __name__)

@controller.route('/api/deployments/<ns>/<dep_name>/services')
def across_namespaces(ns, dep_name):
  broker.check_connected()
  services = DepHelper.services(DepHelper.find(ns, dep_name))
  output = list(map(serialize_service, services))
  return { "data": output }

def serialize_service(s):
  name = s.metadata.name
  namespace = s.metadata.namespace
  port_obj = s.spec.ports[0]
  external_ip = Utils.try_or(lambda: s.status.load_balancer.ingress[0].ip)

  return {
    "name": name,
    "internalIp": s.spec.cluster_ip,
    "externalIp": external_ip,
    "fromPort": port_obj.port,
    "toPort": port_obj.target_port,
    "shortDns": name + "." + namespace,
    "longDns": name + "." + namespace + ".svc.cluster.local",
  }