#!/usr/bin/env python3
from flask import Flask, request, make_response, g
from flask_cors import CORS
import cluster_controller
import debug_controller
import deployments_controller
import run_controller
import status_controller
from debuggers.network_debug import NetworkDebug
from image_changer import ImageChanger

from kube_broker import KubeBroker, BrokerNotConnectedException
from svc_helper import SvcHelper

HOST = '0.0.0.0'
PORT = 5000

broker = KubeBroker()

app = Flask(__name__, static_folder=".", static_url_path="")
app.register_blueprint(status_controller.controller)
app.register_blueprint(deployments_controller.controller)
app.register_blueprint(cluster_controller.controller)
app.register_blueprint(run_controller.controller)
app.register_blueprint(debug_controller.controller)

@app.shell_context_processor
def make_shell_context():
  from pod_helper import PodHelper
  from dep_helper import DepHelper
  from curl_pod import CurlPod
  from image_reloader import ImageReloader

  return {
    'broker': broker,
    'ph': PodHelper,
    'dh': DepHelper,
    'sh': SvcHelper,
    'cp': CurlPod,
    'ir': ImageReloader,
    'ic': ImageChanger,
    'nd': NetworkDebug
  }

@app.errorhandler(BrokerNotConnectedException)
def handle_bad_request(error):
  return {"type": "k8s_api_conn_failed", "reason": str(error)}, 500

app.config["SECRET_KEY"] = "secret!"

CORS(app)

if __name__ == '__main__':
  app.config["cmd"] = ["bash"]
  app.run(host=HOST, debug=True, port=PORT)
