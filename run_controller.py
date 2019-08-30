#!/usr/bin/env python3
from flask import Blueprint, request

from curl_pod import CurlPod
from kube_broker import broker
from utils import Utils

controller = Blueprint('status_controller', __name__)


@controller.route('/api/run/curl', methods=['POST'])
def run_curl_command():
  j_body = request.json
  curl_pod = CurlPod(**j_body)
  raw_curl_response = curl_pod.play()
  return raw_curl_response
