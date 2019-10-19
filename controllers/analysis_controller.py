#!/usr/bin/env python3
from flask import Blueprint, request
from debuggers.network_debug import NetworkDebug

controller = Blueprint('analysis_controller', __name__)

@controller.route('/api/debug/:suite_id/decision_tree')
def decision_tree():
  return { "data": NetworkDebug.tree()['tree'] }

@controller.route('/api/debug/:suite_id/step/:step_id/info')
def step_info(suite_id, step_id):
  pass

@controller.route('/api/debug/:suite/step/:step_id/run')
def step_run():
  pass

