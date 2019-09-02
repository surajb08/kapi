#!/usr/bin/env python3
from flask import Blueprint, request

from curl_pod import CurlPod

controller = Blueprint('run_controller', __name__)

@controller.route('/api/run/curl', methods=['POST'])
def run_curl_command():
  j_body = request.json
  curl_pod = CurlPod(**j_body, pod_name="curl-man", delete_after=False)
  raw_curl_response = curl_pod.run()
  return {'data': raw_curl_response}
