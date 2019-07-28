from kube_apis import coreV1
import utils

POD_STATUS_ACTIVE = 'active'
POD_STATUS_INACTIVE = 'inactive'
LOAD_BALANCER_SERVICE_TYPE = 'LoadBalancer'


def get_load_balancer_service_external_endpoint(returned_service):
    external_host = None
    external_port = None
    external_type = None
    if returned_service.status.load_balancer is not None \
            and returned_service.status.load_balancer.ingress is not None\
            and len(returned_service.status.load_balancer.ingress) > 0:

        first_ingress = returned_service.status.load_balancer.ingress[0]
        if first_ingress.hostname is not None:
            external_host = first_ingress.hostname
        else:
            external_host = first_ingress.ip
    if len(returned_service.spec.ports) > 0:
        external_port = returned_service.spec.ports[0].target_port
        external_type = returned_service.spec.ports[0].protocol

    if external_host is not None and external_port is not None and external_type is not None:
        return {
            "host": external_host,
            "port": external_port,
            "type": external_type
        }

def get_load_balancer_service_internal_endpoint(returned_service):
    internal_host = returned_service.spec.cluster_ip
    internal_port = None
    internal_type = None

    if len(returned_service.spec.ports) > 0:
        internal_port = returned_service.spec.ports[0].node_port
        internal_type = returned_service.spec.ports[0].protocol
    if internal_host is not None and internal_port is not None and internal_type is not None:
        return {
            "host": internal_host,
            "port": internal_port,
            "type": internal_type
        }


def get_deployment_load_balancer_endpoints(match_labels):
    external = None
    internal = None
    match_labels_selector = utils.label_dict_to_kube_api_label_selector(match_labels)
    returned_services = coreV1.list_service_for_all_namespaces(label_selector=match_labels_selector)

    # find the first load balancer service and take the endpoints of that
    for returned_service in returned_services.items:
        if returned_service.spec.type == LOAD_BALANCER_SERVICE_TYPE:
            external = get_load_balancer_service_external_endpoint(returned_service)
            internal = get_load_balancer_service_internal_endpoint(returned_service)
            break

    return (external, internal)


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

    endpoints = {
        "external": None,
        "internal": None
    }
    if deployment.spec.selector.match_labels is not None:
        (external, internal) = get_deployment_load_balancer_endpoints(deployment.spec.selector.match_labels)
        endpoints["external"] = external
        endpoints["internal"] = internal

    return {
        "name": deployment.metadata.name,
        "namespace": deployment.metadata.namespace,
        # "language": String,
        # "githubRepo": String,
        "createdAt": isodate,
        "containers": containers,
        "endpoints": endpoints,
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