#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify
from http import HTTPStatus
import os
import json
from kubernetes import client, config
import utils
from kube_deployment  import get_deployment_details
from kube_apis import  coreV1, extensionsV1Beta

# Configs can be set in Configuration class directly or using helper utilites
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

@app.route('/api/deployments', methods=['GET'])
def get_filtered_deployments():
    namespace_filters_set = set(request.args.getlist('namespace'))
    label_filters_set = set(request.args.getlist('label'))

    response = []
    if len(label_filters_set) == 0:
        response = extensionsV1Beta.list_deployment_for_all_namespaces()
    else:
        kube_label_selector = utils.api_label_filters_to_kube_api_label_selector(label_filters_set)
        response = extensionsV1Beta.list_deployment_for_all_namespaces(label_selector=kube_label_selector)

    received_deployments = list(response.items)

    items = []
    for received_deployment in received_deployments:
        if len(namespace_filters_set) > 0\
                and received_deployment.metadata.namespace not in namespace_filters_set:
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