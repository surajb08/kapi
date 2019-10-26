import base64
import os
import json
from kubernetes import config, client
import subprocess


class BrokerNotConnectedException(Exception):
  def __init__(self, message):
    super().__init__(message)

class KubeBroker:

  def __init__(self):
    self.is_connected = False
    self.last_error = None
    self.coreV1 = None
    self.appsV1Api = None
    self.client = None
    self.batchV1 = None

  def connect(self):
    if os.environ.get('K8S_AUTH_TYPE') == 'local':
      is_connected = self.in_cluster_connect()
    else:
      is_connected = self.out_cluster_connect()

    self.is_connected = is_connected
    self.client = client if is_connected else None
    self.coreV1 = client.CoreV1Api() if is_connected else None
    self.appsV1Api = client.AppsV1Api() if is_connected else None
    self.batchV1 = client.BatchV1Api() if is_connected else None
    return is_connected

  def in_cluster_connect(self):
    try:
      config.load_incluster_config()
      return True
    except Exception as e1:
      self.last_error = e1
      return False

  def out_cluster_connect(self):
    try:
      user_token = KubeBroker.read_user_token()
      configuration = client.Configuration()
      configuration.host="https://34.68.10.10"
      configuration.verify_ssl = False
      configuration.debug = False
      configuration.api_key = { "authorization" : f"Bearer {user_token}" }
      client.Configuration.set_default(configuration)

      import urllib3
      urllib3.disable_warnings()

      return True
    except Exception as e:
      self.last_error = e
      return False

  @staticmethod
  def read_user_token():
    sa_bundle = KubeBroker.jcmd("kubectl get sa/nectar -o json")
    secret_name = sa_bundle['secrets'][0]['name']
    secret_bundle = KubeBroker.jcmd(f"kubectl get secret {secret_name} -o json")
    b64_user_token = secret_bundle['data']['token']
    out = str(base64.b64decode(b64_user_token))[2:-1]
    return out

  @staticmethod
  def jcmd(cmd_str):
    return json.loads(KubeBroker.cmd(cmd_str))

  @staticmethod
  def cmd(cmd_str):
    formatted_cmd = cmd_str.split(' ')
    output = subprocess.run(formatted_cmd, stdout=subprocess.PIPE).stdout
    return output

  def check_connected(self, attempt=True):
    if not self.is_connected:
      if attempt:
        if self.connect():
          return
      raise BrokerNotConnectedException(self.last_error or "unknown")

broker = KubeBroker()
broker.connect()