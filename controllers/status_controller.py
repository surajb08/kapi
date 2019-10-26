#!/usr/bin/env python3
from flask import Blueprint

from actions.docker_ops import DockerOps
from helpers.kube_broker import broker

controller = Blueprint('status_controller', __name__)

@controller.route('/api/status')
def status():
  return status_body()

@controller.route('/api/status/connect')
def connect():
  broker.connect()
  broker.check_connected()
  return status_body()

def status_body():
  return {
    "is_connected": broker.is_connected,
    "last_error": broker.last_error
  }

@controller.route('/api/status/jobs/<job_name>')
def job_logs(job_name):
   job = DockerOps.find_job(job_name)
   if job:
     logs = DockerOps.logs(job)

