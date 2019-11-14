import base64
import os
import json
from kubernetes import config, client
import subprocess
import urllib3

from utils.utils import Utils


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
    self.auth_type = None

  def connect(self, force_type=None):
    auth_type = force_type or self.env_auth_type()
    if auth_type == 'inside':
      is_connected = self.in_cluster_connect()
      self.auth_type = 'local'
    else:
      is_connected = self.out_cluster_connect()
      self.auth_type = 'remote'

    self.is_connected = is_connected
    self.auth_type = self.auth_type if is_connected else None
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
    if Utils.is_prod():
      raise Exception("Out cluster auth not for production!")

    try:
      user_token = KubeBroker.read_target_cluster_user_token()
      configuration = client.Configuration()
      configuration.host = KubeBroker.read_target_cluster_ip()
      configuration.verify_ssl = False
      configuration.debug = False
      configuration.api_key = {"authorization": f"Bearer {user_token}"}
      client.Configuration.set_default(configuration)
      urllib3.disable_warnings()
      return True
    except Exception as e:
      print(f"FAILED TO CONNECT {e}")
      return False

  @staticmethod
  def kubectl():
    return 'kubectl' if Utils.is_dev() else 'microk8s.kubectl'

  @staticmethod
  def read_target_cluster_ip():
    k = KubeBroker.kubectl()
    local_config = KubeBroker.jcmd(f"{k} config view -o json")
    clusters = local_config['clusters']
    target = 'nectar-dev' if Utils.is_dev() else 'microk8s-cluster'
    nectar_dev = [c for c in clusters if c['name'] == target][0]
    return nectar_dev['cluster']['server']

  @staticmethod
  def read_target_cluster_user_token():
    k = KubeBroker.kubectl()
    sa_bundle = KubeBroker.jcmd(f"{k} get sa/nectar -o json")
    secret_name = sa_bundle['secrets'][0]['name']
    secret_bundle = KubeBroker.jcmd(f"{k} get secret {secret_name} -o json")
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

  @staticmethod
  def env_auth_type():
    return os.environ.get('K8S_AUTH_TYPE')

  def check_connected(self, attempt=True):
    if not self.is_connected:
      if attempt:
        if self.connect():
          return
      raise BrokerNotConnectedException(self.last_error or "unknown")

broker = KubeBroker()
broker.connect()