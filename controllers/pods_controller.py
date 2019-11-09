#!/usr/bin/env python3
from flask import Blueprint, request

from helpers.pod_helper import PodHelper

controller = Blueprint('pods_controller', __name__)

@controller.route('/api/pods/<namespace>/<name>/logs')
def logs(namespace, name):
  since_seconds = int(request.args.get('since_seconds', '5000'))
  _logs = PodHelper.read_logs(namespace, name, since_seconds)
  return {"data": _logs}