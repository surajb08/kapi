#!/usr/bin/env python3
from flask import Flask, request, make_response, g
from flask_cors import CORS
from http import HTTPStatus

import broker_controller
import utils

import os
import select
import termios
import struct
import fcntl
import shlex

from kube_apis import KubeBroker

HOST = '0.0.0.0'
PORT = 5000

broker = KubeBroker()

app = Flask(__name__, static_folder=".", static_url_path="")
app.register_blueprint(broker_controller.status_controller)

app.config["SECRET_KEY"] = "secret!"

CORS(app)




if __name__ == '__main__':
  app.config["cmd"] = ["bash"]
  app.run(host=HOST, debug=True, port=PORT)
