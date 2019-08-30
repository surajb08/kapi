#!/usr/bin/env python3
from flask import Blueprint, request

from curl_pod import CurlPod

controller = Blueprint('run_controller', __name__)

@controller.route('/api/run/curl', methods=['POST'])
def run_curl_command():
  print(f"Untouched {request}")
  j_body = request.json
  print(f"The thing {j_body}")
  curl_pod = CurlPod(**j_body)
  raw_curl_response = curl_pod.play()
  return {'response': raw_curl_response}
