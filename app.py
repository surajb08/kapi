#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from http import HTTPStatus
import os
import json
import utils
from kube_deployment import get_deployment_details, delete_deployment_and_matching_services
from kube_apis import coreV1, extensionsV1Beta, client


HOST = '0.0.0.0'
PORT = 5000

app = Flask(__name__)
CORS(app)


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

    response = extensionsV1Beta.list_deployment_for_all_namespaces(field_selector=f'metadata.name={deployment_name}')
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


if __name__ == '__main__':
    app.run(host=HOST, debug=True, port=PORT)
