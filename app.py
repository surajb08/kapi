#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify
from http import HTTPStatus
import os
import json
from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()

coreV1 = client.CoreV1Api()
extensionsV1Beta = client.ExtensionsV1beta1Api()

extensions = client.ExtensionsApi()

ret = coreV1.list_namespace()


HOST = '0.0.0.0'
PORT = 5000

app = Flask(__name__)

def kmd(command):
    return os.popen("kubectl " + command).read()

def kmdy(command):
    return kmd(command + " -o yaml")

def kmdj(command):
    return json.loads(kmd(command + " -o json"))

def simple_deployment(hash):
    return {
        "name": hash['metadata']['name'],
        "expectedPods": hash['spec']['replicas']
        
    }

@app.route('/api/namespaces/<namespace>/deployments/<deployment_name>', methods=['GET'])
def get_namespaced_deployment(namespace, deployment_name):
    response = extensionsV1Beta.list_namespaced_deployment(namespace)
    items = response.items
    matches = list([item for item in items if item.metadata.name == deployment_name])
    if len(matches) == 0:
        make_response({ "message": "Deployment not found"}, HTTPStatus.NOT_FOUND)

    # kuberenetes names are unique: there will be only 1 deployment if any
    deployment = matches[0]
    isodate = deployment.metadata.creation_timestamp.isoformat()

    containers = []
    for container in deployment.spec.template.spec.containers:
        returned_ports = [{"number": port.container_port, "type": port.protocol} for port in container.ports]

        resources = []
        resource_requests = deployment.spec.template.spec.containers[0].resources.requests
        for key in resource_requests.keys():
            resources.append({
                "type": key,
                "requirement": resource_requests[key]
            })

        returned_container = {
            "name": container.name,
            "image": container.image,
            "ports": returned_ports,
            "resources": resources
        }

        containers.append(returned_container)

    return {
        "name": deployment.metadata.name,
        "namespace": namespace,
        # "language": String,
        # "githubRepo": String,
        "createdAt": isodate,
        "containers": containers,
        # endpoints: {
        #     external: {
        #         host: String,
        #         port: Int,
        #         type: String,
        #     },
        #     internal: {
        #         host: String,
        #         port: Int,
        #         type: String,
        #     },
        # },
        # pods: [{
        #     id: String
        #     status: String, ('active', 'inactive')
        # }],
        #"labels": [{id: String, value: String}]
    }


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


@app.route('/yo')
def test():    
    return kmd("get all")


@app.route('/api/deployments/all', methods=['GET'])
def get_deployments_all():
    namespace = request.args.get('namespace') or "default"
    result = kmdj("get deployments --namespace=" + namespace)
    return result

@app.route('/api/deployments', methods=['GET'])
def get_deployments():
    namespace = request.args.get('namespace') or "default"
    result = kmdj("get deployments --namespace=" + namespace)
    cleaned = list(map(simple_deployment, result['items']))
    return { "data": cleaned }

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(host=HOST, debug=True, port=PORT)