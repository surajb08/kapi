#!/usr/bin/env python3
from flask import Blueprint, request

from stunt_pods.curl_pod import CurlPod
from actions.image_changer import ImageChanger
from actions.image_reloader import ImageReloader

controller = Blueprint('run_controller', __name__)

@controller.route('/api/run/curl', methods=['POST'])
def run_curl_command():
  j_body = request.json
  curl_pod = CurlPod(**j_body, pod_name="curl-man", delete_after=False)
  raw_curl_response = curl_pod.run()
  return {'data': raw_curl_response}

@controller.route('/api/run/cmd', methods=['POST'])
def run_command():
  j_body = request.json
  pod = CurlPod(
    pod_name=j_body['pod_name'],
    namespace=j_body['pod_namespace'],
    command=j_body['command'],
    delete_after=False,
  )
  output = pod.run_cmd()
  return { "data": output }

@controller.route('/api/run/image_reload', methods=['POST'])
def image_reload():
  body_args = request.json
  dep_namespace = body_args['dep_namespace']
  dep_name = body_args['dep_name']
  worker = ImageReloader(dep_namespace, dep_name, "reload")
  worker.run()
  return { "data": { 'status': 'working' } }

@controller.route('/api/run/new_image', methods=['POST'])
def new_image():
  body_args = request.json
  dep_namespace = body_args['dep_namespace']
  dep_name = body_args['dep_name']
  target_name = body_args['target_name']
  worker = ImageChanger(dep_namespace, dep_name, target_name)
  worker.run()
  return { "data": { 'status': 'working' } }


@controller.route('/api/run/scale_replicas', methods=['POST'])
def scale_replicas():
  body_args = request.json
  dep_namespace = body_args['dep_namespace']
  dep_name = body_args['dep_name']
  scale_to = int(body_args['scale_to'])
  worker = ImageReloader(dep_namespace, dep_name,  "scale", scale_to)
  worker.run()
  return { "data": { 'status': 'working' } }

@controller.route('/api/run/image_change`', methods=['POST'])
def change_image():
  return { "status": "lol" }
