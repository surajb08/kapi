#!/usr/bin/env python3
import os

import sentry_sdk
from flask import Flask
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration

from controllers import analysis_controller, deployments_controller, run_controller, cluster_controller, \
  status_controller, builds_controller, pods_controller
from actions.image_changer import ImageChanger

from helpers.kube_broker import KubeBroker, BrokerNotConnectedException
from helpers.svc_helper import SvcHelper

HOST = '0.0.0.0'
PORT = 5000

broker = KubeBroker()

if os.environ.get('RUN_ENV') == 'production':
  sentry_sdk.init(
    dsn="https://16c96800cc7442e4b53bb6c04bfe1e84@sentry.io/1796858",
    integrations=[FlaskIntegration()]
  )

app = Flask(__name__, static_folder=".", static_url_path="")
app.register_blueprint(status_controller.controller)
app.register_blueprint(deployments_controller.controller)
app.register_blueprint(cluster_controller.controller)
app.register_blueprint(run_controller.controller)
app.register_blueprint(analysis_controller.controller)
app.register_blueprint(builds_controller.controller)
app.register_blueprint(pods_controller.controller)

@app.shell_context_processor
def make_shell_context():
  from helpers.pod_helper import PodHelper
  from helpers.dep_helper import DepHelper
  from stunt_pods.curl_pod import CurlPod
  from actions.image_reloader import ImageReloader
  from actions.docker_op import DockerOp
  from actions.docker_build_op import DockerBuildOp
  from actions.docker_push_op import DockerPushOp
  from actions.annotator import Annotator

  return {
    'broker': broker,
    'ph': PodHelper,
    'dh': DepHelper,
    'sh': SvcHelper,
    'cp': CurlPod,
    'ir': ImageReloader,
    'ic': ImageChanger,
    'do': DockerOp,
    'DockerBuildOp': DockerBuildOp,
    f"{DockerPushOp.__name__}": DockerPushOp,
    f"{Annotator.__name__}": Annotator
  }

@app.errorhandler(BrokerNotConnectedException)
def handle_bad_request(error):
  return {"type": "k8s_api_conn_failed", "reason": str(error)}, 500

app.config["SECRET_KEY"] = "secret!"

CORS(app)

if __name__ == '__main__':
  app.config["cmd"] = ["bash"]
  app.run(host=HOST, debug=True, port=PORT)
