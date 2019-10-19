#!/usr/bin/env python3
import yaml
from flask import Blueprint

controller = Blueprint('analysis_controller', __name__)

@controller.route('/api/analysis/<suite_id>/decision_tree')
def decision_tree(suite_id):
  fname = f"analysis_suites/{suite_id}/decision_tree.yaml"
  with open(fname, 'r') as stream:
    loaded_dict = yaml.safe_load(stream)
  return { "data": loaded_dict['tree'] }

# @controller.route('/api/analysis/:suite_id/step/:step_id/info')
# def step_info(suite_id, step_id):
#
#   pass
#
# @controller.route('/api/analysis/:suite/step/:step_id/run')
# def step_run():
#   pass
#
