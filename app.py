#!/usr/bin/env python3
from flask import Flask, request, make_response, g
from flask_cors import CORS
from http import HTTPStatus

import cluster_controller
import deployments_controller
import services_controller
import status_controller

from kube_broker import KubeBroker, BrokerNotConnectedException

HOST = '0.0.0.0'
PORT = 5000

broker = KubeBroker()

app = Flask(__name__, static_folder=".", static_url_path="")
app.register_blueprint(status_controller.controller)
app.register_blueprint(deployments_controller.controller)
app.register_blueprint(services_controller.controller)
app.register_blueprint(cluster_controller.controller)

@app.errorhandler(BrokerNotConnectedException)
def handle_bad_request(error):
  print("HANDLING THE EX")
  return {"type": "k8s_api_conn_failed", "reason": str(error)}, 500

app.config["SECRET_KEY"] = "secret!"

CORS(app)

if __name__ == '__main__':
  app.config["cmd"] = ["bash"]
  app.run(host=HOST, debug=True, port=PORT)
