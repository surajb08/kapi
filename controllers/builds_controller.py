#!/usr/bin/env python3
import importlib

import inflection
from flask import Blueprint, request

from actions.docker_build_op import DockerBuildOp
from actions.docker_push_op import DockerPushOp

controller = Blueprint('builds_controller', __name__)

@controller.route('/api/docker/build_image', methods=['POST'])
def build_image():
  args = request.json
  operation = DockerBuildOp(
    repo_tar_url=args['repo_tar_url'],
    dockerfile_path=args['dockerfile_path'],
    output_img=args['output_img']
  )

  operation.create_work_pod()
  return new_job_bundle(operation)

@controller.route('/api/docker/push_image', methods=['POST'])
def push_image():
  args = request.json
  operation = DockerPushOp(
    username=args['username'],
    password=args['password'],
    image_name=args['image_name']
  )
  operation.create_work_pod()
  return new_job_bundle(operation)


@controller.route('/api/docker/<job_type>/<job_id>/job_info')
def job_info(job_type, job_id):
  module_name = f"actions.{job_type}"
  class_name = inflection.camelize(job_type, True)
  loaded_module = importlib.import_module(module_name)
  klass = getattr(loaded_module, class_name)
  instance = klass.find(job_id)
  return {
    'logs': instance.logs().split("\n"),
    'status': instance.status()
  }

def new_job_bundle(operation):
  return {
    'job_id': operation.pod_name,
    'job_type': inflection.underscore(operation.__class__.__name__)
  }

