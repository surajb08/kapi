from kubernetes import config


class KubeBroker:

  def __init__(self):
    self.is_connected = False
    self.last_error = None

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
