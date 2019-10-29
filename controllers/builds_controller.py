#!/usr/bin/env python3
from flask import Blueprint, request

from actions.docker_op import DockerOp

controller = Blueprint('build_controller', __name__)

@controller.route('/api/build/new-image', methods=['POST'])
def build_new_image():
  args = request.json
  operation = DockerOp(
    body
  )
  return {}

def push_image():
  pass

def status():
  pass
