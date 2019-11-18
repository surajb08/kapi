#!/usr/bin/env python3
from flask import Blueprint, request

from k8_kat.base.k8_kat import K8kat

controller = Blueprint('pods_controller', __name__)

@controller.route('/api/pods/<ns>/<name>/logs')
def logs(ns, name):
  pod = K8kat.pods().ns(ns).find(name)
  since_seconds = int(request.args.get('since_seconds', '5000'))
  return dict(data=pod.logs(since_seconds))
