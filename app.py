#!/usr/bin/env python3
from flask import Flask, request, make_response, render_template
from flask_cors import CORS
from http import HTTPStatus
import utils

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

from kube_deployment import get_deployment_details, delete_deployment_and_matching_services,\
    get_deployment_external_internal_endpoints,\
    run_curl_from_test_deployment
from kube_apis import coreV1, extensionsV1Beta
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream


HOST = '0.0.0.0'
PORT = 5000

app = Flask(__name__, template_folder=".", static_folder=".", static_url_path="")
app.config["SECRET_KEY"] = "secret!"

# app.config["child_pid"] = None
CORS(app)

# contains a all ssh sessions initiated by users.
ssh_sessions = {}


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


@app.route('/api/deployments/<deployment_name>/services', methods=['GET'])
def get_deployment_services(deployment_name):
    response = extensionsV1Beta.list_deployment_for_all_namespaces(field_selector=f'metadata.name={deployment_name}')
    matches = list(response.items)
    if len(matches) == 0:
        return make_response({"message": f'Deployment "{deployment_name}" not found'}, HTTPStatus.NOT_FOUND)

    # names are unique
    deployment = matches[0]
    match_labels = deployment.spec.selector.match_labels
    match_labels_selector = utils.label_dict_to_kube_api_label_selector(match_labels)

    returned_services = coreV1.list_service_for_all_namespaces(label_selector=match_labels_selector)
    services = []
    for returned_service in returned_services.items:
        services.append({
            "name": returned_service.metadata.name
        })

    return {
        "items": services,
        "total": len(services)
    }

@app.route('/api/namespaces/<namespace>/deployments/<deployment_name>', methods=['DELETE'])
def delete_deployment(namespace, deployment_name):
    response = extensionsV1Beta.list_namespaced_deployment(namespace, field_selector=f'metadata.name={deployment_name}')
    matches = list(response.items)
    if len(matches) == 0:
        return make_response({"message": f'Deployment "{deployment_name}" not found'}, HTTPStatus.NOT_FOUND)

    # names are unique
    deployment = matches[0]
    delete_deployment_and_matching_services(deployment)

    return make_response({"name": deployment_name })


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


@app.route('/api/namespaces/<namespace>/pods/<pod_name>/run_cmd', methods=['POST'])
def run_pod_command(namespace, pod_name):
    json_body = request.json
    command = json_body["command"]
    print(f"Running command on pod {pod_name} in namespace {namespace} - '{command}'")

    exec_command = shlex.split(command)
    print(f"List format command: {exec_command}")
    response = stream(coreV1.connect_get_namespaced_pod_exec, pod_name, namespace,
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False)

    print("Command response: " + response)
    return {
        "result": response
    }


ALLOWED_HTTP_METHODS = {"POST", "PUT", "PATCH", "DELETE", "GET"}

CURL_RUNNER_DEPLOYMENT = "curl-test"
CURL_TIMEOUT_SECONDS = "30"

@app.route('/api/namespaces/<namespace>/deployments/<deployment_name>/http_request', methods=['POST'])
def run_curl_command(namespace, deployment_name):
    json_body = request.json
    http_method = json_body["method"]
    request_path = json_body["path"]
    request_headers = json_body["headers"]
    request_body = json_body["body"]

    if http_method not in ALLOWED_HTTP_METHODS:
        return make_response({"message": f"HTTP method {http_method} not supported."}, HTTPStatus.BAD_REQUEST)

    response = extensionsV1Beta.list_namespaced_deployment(namespace, field_selector=f'metadata.name={deployment_name}')
    matches = list(response.items)
    if len(matches) == 0:
        return make_response({"message": f'Deployment "{deployment_name}" not found'}, HTTPStatus.NOT_FOUND)
    target_deployment = matches[0]
    (external, internal) = get_deployment_external_internal_endpoints(target_deployment.spec.selector.match_labels)
    if internal is None:
        return make_response({"message": f'Deployment "{deployment_name}" does not have an internal host and port.'}, HTTPStatus.CONFLICT)
    internal_host = internal["host"]
    internal_port = internal["port"]
    request_host = f"{internal_host}:{internal_port}{request_path}"
    print(f"The request host being targeted is {request_host}")

    exec_command = utils.curl_params_to_curl_exec_command(
        request_host, http_method, request_headers, request_body, CURL_TIMEOUT_SECONDS)

    raw_curl_response = run_curl_from_test_deployment(namespace, CURL_RUNNER_DEPLOYMENT, exec_command)

    try:
        parsed_curl_response = utils.parse_curl_code_headers_body_output(raw_curl_response)
        return parsed_curl_response
    except:
        err = f"Failed to parse raw curl response {raw_curl_response}"
        print(err)
        return make_response({"message": err}, HTTPStatus.INTERNAL_SERVER_ERROR)


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
def containersshpage():
    return render_template("containersshpage.html")

@app.route("/logstreamdemopage")
def logstreamdemopage():
    return render_template("logstreamdemopage.html")

@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    """write to the child pty. The pty sees this as if you are typing in a real
    terminal.
    """

    currentSocketId = request.sid
    if currentSocketId not in ssh_sessions:
        print(f"Unknown session id '{currentSocketId}'. This should not happen")
        return
    session = ssh_sessions[currentSocketId]
    fd = session["fd"]
    print(f"Receiving INPUT for FD ${fd} and SOCKETID {currentSocketId}")
    if fd:
        # print("writing to ptd: %s" % data["input"])
        os.write(fd, data["input"].encode())


@socketio.on("resize", namespace="/pty")
def resize(data):
    currentSocketId = request.sid
    if currentSocketId not in ssh_sessions:
        print(f"Unknown session id '{currentSocketId}'. This should not happen")
        return
    session = ssh_sessions[currentSocketId]
    fd = session["fd"]
    print(f"Receiving RESIZE for FD ${fd} and SOCKETID {currentSocketId}")
    if fd:
        set_winsize(fd, data["rows"], data["cols"])


@socketio.on("connect", namespace="/pty")
def connect():
    """new client connected"""

    pod_name = request.args.get('podName')
    pod_namespace = request.args.get('podNamespace')
    print(f"Requesting connection to pod {pod_name} in namespace {pod_namespace}")
    try:
        resp = coreV1.read_namespaced_pod(name=pod_name,
                                       namespace=pod_namespace)
    except ApiException as e:
        if e.status != 404:
            print("Unknown error: %s" % e)
            return False
        print("Error: Pod not found")
        return False

    # create child process attached to a pty we can read from and write to
    (child_pid, fd) = pty.fork()
    if child_pid == 0:
        # this is the child process fork.
        # anything printed here will show up in the pty, including the output
        # of this subprocess
        subprocess.run(app.config["cmd"])
    else:
        currentSocketId = request.sid

        print(f"Creating session with FD ${fd}  and SOCKETID {currentSocketId} for pod connection ${pod_name}")
        ssh_sessions[currentSocketId] = {
            "fd": fd,
            "child_pid": child_pid,
            "pod_name": pod_name,
            "namespace": pod_namespace
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

        print(f"ssh-ing into remote pod {pod_name}")

        pod_ssh_command = f'source shell_to_pod.sh "{pod_name}"\n'
        os.write(fd, pod_ssh_command.encode())



SOCKETIO_DEPLOYMENT_LOGS_NAMESPACE = "/deployment-logs"

logs_sessions = {}

def read_and_forward_kubectl_logs(session_id, kubectl_process):
    for line in iter(kubectl_process.stdout.readline, b''):
        socketio.sleep(0.01)
        print(f"Sending log line to receiver {line}")
        decoded_line = line.decode("utf-8")
        socketio.emit("deployment-logs-output",
                      {"output": decoded_line},
                      namespace=SOCKETIO_DEPLOYMENT_LOGS_NAMESPACE,
                      room=session_id)
    # process.communicate()


@socketio.on("connect", namespace=SOCKETIO_DEPLOYMENT_LOGS_NAMESPACE)
def on_deployment_logs_connect():
    deployment_name = request.args.get('deploymentName')
    namespace = request.args.get('deploymentNamespace')
    print(f"Attempting to stream logs for ${deployment_name}")
    try:
        response = extensionsV1Beta.list_namespaced_deployment(namespace, field_selector=f'metadata.name={deployment_name}')
        matches = list(response.items)
        if len(matches) == 0:
            print(f"Failed to find deployment {deployment_name}")
            return False
    except ApiException as e:
        if e.status != 404:
            print("Unknown error: %s" % e)
            return False
        print("Error: Pod not found")
        return False

    session_id = request.sid

    kubectl_process = subprocess.Popen(['kubectl', "logs", "-f", "deployment/frontend"], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    logs_sessions[session_id] = {
        "kubectl_process": kubectl_process,
        "deployment_name": deployment_name,
        "namespace": namespace
    }

    def run_read_and_forward_kubectl_logs():
        read_and_forward_kubectl_logs(session_id, kubectl_process)
    socketio.start_background_task(target=run_read_and_forward_kubectl_logs)

@socketio.on("disconnect",  namespace=SOCKETIO_DEPLOYMENT_LOGS_NAMESPACE)
def on_deployment_logs_disconnect():
    session_id = request.sid
    print(f"Received 'disconnect' from {session_id}")

    session = logs_sessions[session_id]
    print(f"Killing kubectl process..")
    session["kubectl_process"].kill()

    del logs_sessions[session_id]
    print("Disconnected successfully for {session_id}")


if __name__ == '__main__':
    app.config["cmd"] = ["bash"]
    socketio.run(app, debug=True, port=PORT)
    app.run(host=HOST, debug=True, port=PORT)
