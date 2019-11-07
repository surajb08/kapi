#!/usr/bin/env python3
from flask import Blueprint, request
import dateutil.parser


from helpers.pod_helper import PodHelper

controller = Blueprint('pods_controller', __name__)

@controller.route('/api/pods/<namespace>/<name>/logs')
def annotate(namespace, name):
  timestamp_str = request.args.get('timestamp')
  then = dateutil.parser.parse(timestamp_str)

  logs = PodHelper.logs_since(namespace, name, then)
  return {"logs": logs.split("\n")}
