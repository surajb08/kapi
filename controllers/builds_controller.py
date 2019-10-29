#!/usr/bin/env python3
import importlib

import inflection
from flask import Blueprint, request

from actions.docker_build_op import DockerBuildOp

controller = Blueprint('build_controller', __name__)

@controller.route('/api/docker/build_image', methods=['POST'])
def build_image():
  args = request.json
  operation = DockerBuildOp(
    zip_url=args['zip_url'],
    df_path=args['df_path'],
    out_name=args['out_name']
  )

  operation.create_work_pod()

  return {
    'job_id': operation.pod_name,
    'job_type': inflection.underscore(operation.__class__.__name__)
  }

@controller.route('/api/docker/<job_type>/<job_id>/job_info')
def job_info(job_type, job_id):
  module_name = f"actions.{job_type}"
  class_name = inflection.camelize(job_type, True)
  loaded_module = importlib.import_module(module_name)
  klass = getattr(loaded_module, class_name)
  instance = klass.find(job_id)
  return {
    'logs': instance.logs(),
    'status': None
  }

def push_image():
  pass

def status():
  pass
