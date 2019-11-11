#!/usr/bin/env python3
import os

from flask import Blueprint, request

from helpers.dep_helper import DepHelper
from helpers.kube_broker import broker

controller = Blueprint('status_controller', __name__)

@controller.route('/api/status')
def status():
  return status_body()

@controller.route('/api/status/restart', methods=['POST'])
def restart():
  DepHelper.restart_nectar_deps(request.json['deployments'])
  return { "status": "working" }

@controller.route('/api/status/connect')
def connect():
  broker.connect()
  broker.check_connected()
  return status_body()

def status_body():
  return {
    "think_am_connected": broker.is_connected,
    "auth_type": broker.auth_type,
    "auth_type_var": broker.env_auth_type(),
    "sanity": '1'
  }

@controller.route('/api/status/revision')
def revision():
  return{
    "sha": os.environ.get('REVISION')
  }