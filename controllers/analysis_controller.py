#!/usr/bin/env python3
import yaml
from flask import Blueprint, request

from analysis_suites.network.network_suite import NetworkSuiteStep, ServiceConnectsStep

controller = Blueprint('analysis_controller', __name__)

@controller.route('/api/analysis/<suite_id>/decision_tree')
def decision_tree(suite_id):
  fname = f"analysis_suites/{suite_id}/decision_tree.yaml"
  with open(fname, 'r') as stream:
    loaded_dict = yaml.safe_load(stream)
  return { "data": loaded_dict['tree'] }

@controller.route('/api/analysis/<suite_id>/step/<step_id>/info', methods=['POST'])
def step_info(suite_id, step_id):
  step = load_requested_step()

  return {
    "summary": step.summary_copy(),
    "sub_steps": step.steps_copy()
  }

def load_requested_step():
  j_body = request.json
  print(f"THIS IS ME {j_body}")
  return ServiceConnectsStep(**j_body)


# @controller.route('/api/analysis/:suite/step/:step_id/run')
# def step_run():
#   pass
#
