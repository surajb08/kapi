#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify, render_template
from flask_cors import CORS
from http import HTTPStatus
import os
import json
import utils
from kube_deployment import get_deployment_details
from kube_apis import coreV1, extensionsV1Beta

# container ssh specific imports
from flask_socketio import SocketIO
import pty
import os
import subprocess
import select
import termios
import struct
import fcntl
import shlex


HOST = '0.0.0.0'
PORT = 5000

app = Flask(__name__, template_folder=".", static_folder=".", static_url_path="")
app.config["SECRET_KEY"] = "secret!"

# app.config["child_pid"] = None
CORS(app)


sessions = {}


def simple_deployment(hash):
    return {
        "name": hash['metadata']['name'],
        "expectedPods": hash['spec']['replicas']
    }

@app.route('/api/deployments', methods=['GET'])
def get_filtered_deployments():
    namespace_filters_set = set(request.args.getlist('namespace'))
    label_filters_set = set(request.args.getlist('label'))

    response = extensionsV1Beta.list_deployment_for_all_namespaces()
    received_deployments = list(response.items)

    label_filters_dict = {}
    if len(label_filters_set) > 0:
        try:
            label_filters_dict = utils.api_label_filters_to_dict(list(label_filters_set))
        except:
            return make_response({"message": 'Malformed label filters'}, HTTPStatus.BAD_REQUEST)

    items = []
    for received_deployment in received_deployments:
        if len(namespace_filters_set) > 0\
                and received_deployment.metadata.namespace not in namespace_filters_set:
            continue

        if len(label_filters_dict) > 0:
            if received_deployment.spec.selector.match_labels is not None:
                matches_at_least_one_label = False
                for key, value in label_filters_dict.items():
                    if key in received_deployment.spec.selector.match_labels and\
                            received_deployment.spec.selector.match_labels[key] in value:
                        matches_at_least_one_label = True
                        break
                if not matches_at_least_one_label:
                    continue
            else:
                # label filters are defined but it has none
                continue

        detailed_deployment = get_deployment_details(received_deployment)
        items.append(detailed_deployment)

    return {
        "items": items,
        "total": len(items)
    }

@app.route('/api/deployments/<deployment_name>', methods=['GET'])
def get_deployment(deployment_name):
    response = extensionsV1Beta.list_deployment_for_all_namespaces(field_selector=f'metadata.name={deployment_name}')
    matches = list(response.items)
    if len(matches) == 0:
        return make_response({ "message": f'Deployment "{deployment_name}" not found'}, HTTPStatus.NOT_FOUND)

    # kuberenetes names are unique: there will be only 1 deployment if any
    deployment = matches[0]
    detailed_deployment = get_deployment_details(deployment)
    return detailed_deployment

@app.route('/api/namespaces/<namespace>/deployments', methods=['GET'])
def get_namespaced_deployments(namespace):
    response = extensionsV1Beta.list_namespaced_deployment(namespace)
    matches = list(response.items)

    items = []
    for match in matches:
        # TODO: can execute this concurrently to speed up the endpoint
        detailed_deployment = get_deployment_details(match)
        items.append(detailed_deployment)

    return {
        "items": items,
        "total": len(items)
    }

@app.route('/api/namespaces/<namespace>/deployments/<deployment_name>', methods=['GET'])
def get_namespaced_deployment(namespace, deployment_name):
    response = extensionsV1Beta.list_namespaced_deployment(namespace, field_selector=f'metadata.name={deployment_name}')
    matches = list(response.items)
    if len(matches) == 0:
        return make_response({"message": f'Deployment "{deployment_name}" not found'}, HTTPStatus.NOT_FOUND)

    # kuberenetes names are unique: there will be only 1 deployment if any
    deployment = matches[0]
    detailed_deployment = get_deployment_details(deployment)
    return detailed_deployment


@app.route('/api/namespaces', methods=['GET'])
def get_namespaces():
    response = coreV1.list_namespace()
    items = response.items
    namespaces = list([{"name": namespace.metadata.name} for namespace in items])
    return {
        "items": namespaces,
        "total": len(namespaces)
    }

@app.route('/')
def hello():
    return "<h1>Hello worlds</h1>"

socketio = SocketIO(app)

def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def read_and_forward_pty_output(fd, session_id):
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        if fd:
            timeout_sec = 0
            (data_ready, _, _) = select.select([fd], [], [], timeout_sec)
            if data_ready:
                output = os.read(fd, max_read_bytes).decode()
                socketio.emit("pty-output", {"output": output}, namespace="/pty", room=session_id)


@app.route("/containersshpage")
def index():
    return render_template("index.html")


@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    """write to the child pty. The pty sees this as if you are typing in a real
    terminal.
    """

    currentSocketId = request.sid
    if currentSocketId not in sessions:
        print(f"Unknown session id '{currentSocketId}'. This should not happen")
        return
    session = sessions[currentSocketId]
    fd = session["fd"]
    print(f"Receiving INPUT for FD ${fd} and SOCKETID {currentSocketId}")
    if fd:
        # print("writing to ptd: %s" % data["input"])
        os.write(fd, data["input"].encode())


@socketio.on("resize", namespace="/pty")
def resize(data):
    currentSocketId = request.sid
    if currentSocketId not in sessions:
        print(f"Unknown session id '{currentSocketId}'. This should not happen")
        return
    session = sessions[currentSocketId]
    fd = session["fd"]
    print(f"Receiving RESIZE for FD ${fd} and SOCKETID {currentSocketId}")
    if fd:
        set_winsize(fd, data["rows"], data["cols"])


@socketio.on("connect", namespace="/pty")
def connect():
    """new client connected"""
    #
    # if app.config["child_pid"]:
    #     # already started child process, don't start another
    #     return

    # create child process attached to a pty we can read from and write to
    (child_pid, fd) = pty.fork()
    if child_pid == 0:
        # this is the child process fork.
        # anything printed here will show up in the pty, including the output
        # of this subprocess
        subprocess.run(app.config["cmd"])
    else:
        # this is the parent process fork.
        # store child fd and pid
        # app.config["fd"] = fd
        # app.config["child_pid"] = child_pid

        currentSocketId = request.sid
        print(f"Creating session with FD ${fd}  and SOCKETID {currentSocketId}")
        sessions[currentSocketId] = {
            "fd": fd,
            "child_pid": child_pid
        }

        set_winsize(fd, 50, 50)
        cmd = " ".join(shlex.quote(c) for c in app.config["cmd"])
        print("child pid is", child_pid)
        print(
            f"starting background task with command `{cmd}` to continously read "
            "and forward pty output to client"
        )

        def run_read_and_forward():
            read_and_forward_pty_output(fd, currentSocketId)
        socketio.start_background_task(target=run_read_and_forward)
        print("task started")


if __name__ == '__main__':
    app.config["cmd"] = ["bash"]
    socketio.run(app, debug=True, port=PORT)
    app.run(host=HOST, debug=True, port=PORT)
