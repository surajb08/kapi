#!/usr/bin/env python3

from flask import Flask, request, jsonify
from kubernetes import config, client
from typing import List

config.load_kube_config()
COREV1API = client.CoreV1Api()
APPSV1API = client.AppsV1Api()

HOST = '0.0.0.0'
PORT = 5000

# initialize flask application
app = Flask(__name__)

# sample hello world page
@app.route('/')
def hello():
    return "<h1>Hello World</h1>"

@app.route('/api/namespace', methods=['GET'])
def get_namespaces():
    namespaces = COREV1API.list_namespace()
    return jsonify({
        "namespaces": [
            namespace.metadata.name 
            for namespace in namespaces.items 
            if namespace.metadata.name not in ["kube-system", "kube-public"]
        ]
    })

@app.route('/api/deployments', methods=['GET'])
def get_deployments():
    res = {}
    namespace = request.args.get('namespace')
    if not namespace:
        return jsonify({})
    print("Namespace requested %s", namespace)
    deployments = APPSV1API.list_namespaced_deployment(namespace)
    for deployment in deployments.items:
        name = deployment.metadata.name
        res[name] = []
        for container in deployment.spec.template.spec.containers:
            res[name].append({container.name: container.image})
    return jsonify(res)

if __name__ == '__main__':
    app.run(host=HOST, debug=True, port=PORT)
