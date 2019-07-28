from kube_apis import coreV1
import utils

POD_STATUS_ACTIVE = 'active'
POD_STATUS_INACTIVE = 'inactive'

def get_deployment_details(deployment):
    isodate = deployment.metadata.creation_timestamp.isoformat()

    containers = []
    for container in deployment.spec.template.spec.containers:

        returned_ports = []
        if container.ports is not None:
            returned_ports = [{"number": port.container_port, "type": port.protocol} for port in container.ports]

        resources = []
        resource_requests = container.resources.requests

        if resource_requests is not None:
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

    returned_pods = []
    if deployment.spec.selector.match_labels is not None:
        match_labels_selector = utils.label_dict_to_kube_api_label_selector(deployment.spec.selector.match_labels)
        returned_pods = coreV1.list_pod_for_all_namespaces(label_selector=match_labels_selector)

    pods = []
    for returned_pod in returned_pods.items:
        pod_status = POD_STATUS_ACTIVE if returned_pod.status.phase == 'Running' else POD_STATUS_ACTIVE
        pods.append({
            "name": returned_pod.metadata.name,
            "status": pod_status
        })

    return {
        "name": deployment.metadata.name,
        "namespace": deployment.metadata.namespace,
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
        "pods": pods,
        "labels": deployment.spec.selector.match_labels
    }