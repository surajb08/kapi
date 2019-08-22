from kubernetes import config, client


class BrokerNotConnectedException(Exception):
  def __init__(self, message, errors):
    super().__init__(message)
    self.errors = errors

class KubeBroker:

  def __init__(self):
    self.is_connected = False
    self.last_error = None
    self.coreV1 = None
    self.appsV1Api = None

  def connect(self):
    is_connected = False
    error = None
    try:
      config.load_incluster_config()
      is_connected = True
    except Exception as e1:
      error = e1
      try:
        config.load_kube_config()
        is_connected = True
      except Exception as e2:
        error = e2

    self.is_connected = is_connected
    self.last_error = str(error) if not is_connected else None
    self.coreV1 = client.CoreV1Api() if is_connected else None
    self.appsV1Api = client.AppsV1Api() if is_connected else None

  def check_connected(self):
    if not self.is_connected:
      raise BrokerNotConnectedException(self.last_error)

broker = KubeBroker()
broker.connect()