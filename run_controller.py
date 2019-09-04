#!/usr/bin/env python3
from flask import Blueprint, request

from curl_pod import CurlPod
from image_reloader import ImageReloader

controller = Blueprint('run_controller', __name__)

@controller.route('/api/run/curl', methods=['POST'])
def run_curl_command():
  j_body = request.json
  curl_pod = CurlPod(**j_body, pod_name="curl-man", delete_after=False)
  raw_curl_response = curl_pod.run()
  return {'data': raw_curl_response}

@controller.route('/api/run/image_reload', methods=['POST'])
def image_reload():
  body_args = request.json
  dep_namespace = body_args['dep_namespace']
  dep_name = body_args['dep_name']
  worker = ImageReloader(dep_namespace, dep_name)
  worker.run()
  return { "data": { 'status': 'working' } }


@controller.route('/api/run/image_change`', methods=['POST'])
def change_image():
  return { "status": "lol" }
