#!/usr/bin/env python3
import importlib

import inflection
import yaml
from flask import Blueprint, request

controller = Blueprint('analysis_controller', __name__)

@controller.route('/api/analysis/<suite_id>/decision_tree')
def decision_tree(suite_id):
  fname = f"analysis_suites/{suite_id}/decision_tree.yaml"
  with open(fname, 'r') as stream:
    loaded_dict = yaml.safe_load(stream)
  return {"data": loaded_dict['tree']}

@controller.route('/api/analysis/<suite_id>/step/<step_id>/info', methods=['POST'])
def step_info(suite_id, step_id):
  step = load_requested_step(suite_id, step_id)

  return {
    "summary": step.summary_copy(),
    "sub_steps": step.steps_copy()
  }

@controller.route('/api/analysis/<suite_id>/step/<step_id>/run', methods=['POST'])
def run_step(suite_id, step_id):
  pass

def load_requested_step(suite, step):
  j_body = request.json
  class_name = inflection.camelize(f"{step}_step", True)
  module_name = f"analysis_suites.{suite}.{step}_step"
  loaded_module = importlib.import_module(module_name)
  step_class = getattr(loaded_module, class_name)
  return step_class(**j_body)


# @controller.route('/api/analysis/:suite/step/:step_id/run')
# def step_run():
#   pass
#
