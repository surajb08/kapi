#!/usr/bin/env python3

import requests
from flask import Flask, request, jsonify
from typing import List
import os
import json

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