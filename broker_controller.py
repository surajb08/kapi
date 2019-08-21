#!/usr/bin/env python3
from flask import Flask, Blueprint

from kube_apis import KubeBroker

status_controller = Blueprint('status_controller', __name__)
broker = KubeBroker()


@status_controller.route('/api/status')
def status():
  return status_body()


@status_controller.route('/api/connect')
def connect():
  broker.connect()
  return status_body()


def status_body():
  return {
    "is_connected": broker.is_connected,
    "last_error": broker.last_error
  }
