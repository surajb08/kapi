#!/usr/bin/env python3
from flask import Blueprint, request
from debuggers.network_debug import NetworkDebug

controller = Blueprint('debug_controller', __name__)

@controller.route('/api/debug/network/decision_tree')
def decision_tree():
  return { "data": NetworkDebug.tree()['tree'] }

@controller.route('/api/debug/network/static', methods=['POST'])
def static_checks():
  j_body = request.json
  dbg = NetworkDebug(**j_body)

  answers = [
    dbg.check_service_type(),
    dbg.check_port_types(),
    dbg.check_port_parity()
  ]





def pod_checks():
  3