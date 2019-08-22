#!/usr/bin/env python3
from flask import Flask, request, make_response, g
from flask_cors import CORS
from http import HTTPStatus

import deployments_controller
import status_controller

from kube_broker import KubeBroker

HOST = '0.0.0.0'
PORT = 5000

broker = KubeBroker()

app = Flask(__name__, static_folder=".", static_url_path="")
app.register_blueprint(status_controller.controller)
app.register_blueprint(deployments_controller.controller)

app.config["SECRET_KEY"] = "secret!"

CORS(app)




if __name__ == '__main__':
  app.config["cmd"] = ["bash"]
  app.run(host=HOST, debug=True, port=PORT)
