from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
# config.load_kube_config()
try:
    config.load_incluster_config()
except:
    config.load_kube_config()

coreV1 = client.CoreV1Api()
extensionsV1Beta = client.ExtensionsV1beta1Api()
extensions = client.ExtensionsApi()
appsV1beta1Api = client.AppsV1beta1Api()

ret = coreV1.list_namespace()
