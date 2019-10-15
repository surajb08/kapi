#!/usr/bin/env python3
from flask import Blueprint, request

from curl_pod import CurlPod
from debuggers.network_debug import NetworkDebug
from image_changer import ImageChanger
from image_reloader import ImageReloader

controller = Blueprint('debug_controller', __name__)

@controller.route('/api/debug/', methods=['POST'])
def static_checks():
  j_body = request.json
  df_port = j_body.pop('dockerfile_port')
  dbg = NetworkDebug(**j_body)

  answers = [
    dbg.check_service_type(),
    dbg.check_port_types(),
    dbg.check_port_parity(df_port)
  ]

  return { 'data': answers }