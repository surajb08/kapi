from kube_apis import coreV1, extensionsV1Beta, client, appsV1beta1Api
import utils
from kubernetes.stream import stream
from typing import List

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

        # assume that we only have 1 ingress that's relevant here
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
        port_data = returned_service.spec.ports[0]
        internal_port = port_data.port
        internal_type = returned_service.spec.ports[0].protocol
    if internal_host is not None and internal_port is not None and internal_type is not None:
        return {
            "host": internal_host,
            "port": internal_port,
            "type": internal_type
        }

def get_nodeport_service_internal_endpoint(returned_service):
    internal_host = returned_service.spec.cluster_ip
    internal_port = None
    internal_type = None

    if len(returned_service.spec.ports) > 0:
        port_data = returned_service.spec.ports[0]
        if port_data.node_port is not None:
            internal_port = port_data.node_port
        else:
            internal_port = port_data.port
        internal_type = returned_service.spec.ports[0].protocol
    if internal_host is not None and internal_port is not None and internal_type is not None:
        return {
            "host": internal_host,
            "port": internal_port,
            "type": internal_type
        }

def get_deployment_external_internal_endpoints(match_labels):
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

    if external is None and internal is None:
        # couldn't find a load balancer
        for returned_service in returned_services.items:
            internal = get_nodeport_service_internal_endpoint(returned_service)
            if internal is not None:
                break

    return (external, internal)


def get_deployment_containers(returned_containers):
    containers = []
    for container in returned_containers:

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
    return containers

def get_deployment_details(deployment):
    isodate = deployment.metadata.creation_timestamp.isoformat()

    containers = get_deployment_containers(deployment.spec.template.spec.containers)

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
        (external, internal) = get_deployment_external_internal_endpoints(deployment.spec.selector.match_labels)
        endpoints["external"] = external
        endpoints["internal"] = internal

    return {
        "name": deployment.metadata.name,
        "namespace": deployment.metadata.namespace,
        # TODO: implement the following fields by using the github-kubernetes correlation logic
        # "language": String,
        # "githubRepo": String,
        "createdAt": isodate,
        "containers": containers,
        "endpoints": endpoints,
        "pods": pods,
        "labels": deployment.spec.selector.match_labels
    }

def delete_deployment_and_matching_services(deployment):
    deployment_name = deployment.metadata.name
    namespace = deployment.metadata.namespace
    match_labels = deployment.spec.selector.match_labels
    match_labels_selector = utils.label_dict_to_kube_api_label_selector(match_labels)

    print("Deleting services..")
    returned_services = coreV1.list_service_for_all_namespaces(label_selector=match_labels_selector)

    for returned_service in returned_services.items:
        service_name = returned_service.metadata.name
        service_namespace = returned_service.metadata.namespace
        print(f"Deleting service {service_name} within namespace {service_namespace}")
        api_response = coreV1.delete_namespaced_service(
            name=service_name,
            namespace=service_namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
                grace_period_seconds=5))
        print(f"Service deleted. status='{str(api_response.status)}'")

    print(f"Services linked to deployment {deployment_name} under namespace {namespace} are deleted.")

    print(f"Deleting deployment {deployment_name} under namespace {namespace}")
    api_response = extensionsV1Beta.delete_namespaced_deployment(
        name=deployment_name,
        namespace=namespace,
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    print(f"Deployment deleted. status='{str(api_response.status)}'")

def create_test_curl_deployment_object(deployment_name: str):
    container = client.V1Container(
        name="busybox-curl",
        image="yauritux/busybox-curl",
        # make it run forever so it can receive curls as needed
        command=[ "/bin/sh", "-ce", "tail -f /dev/null" ])
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "busybox-curl"}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    spec = client.AppsV1beta1DeploymentSpec(
        replicas=1,
        template=template)
    # Instantiate the deployment object
    deployment = client.AppsV1beta1Deployment(
        api_version="apps/v1beta1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=deployment_name),
        spec=spec)

    return deployment


def create_deployment(deployment):
    api_response = appsV1beta1Api.create_namespaced_deployment(
        body=deployment,
        namespace="default")
    print("Deployment created. status='%s'" % str(api_response.status))
    return api_response


def run_curl_from_test_deployment(namespace: str, deployment_name: str, exec_command: List[str]):
    response = extensionsV1Beta.list_namespaced_deployment(namespace, field_selector=f'metadata.name={deployment_name}')
    matches = list(response.items)
    if len(matches) == 0:
        print(f"The curl test deployment {deployment_name} does not exist yet. Creating..")
        deployment_object = create_test_curl_deployment_object(deployment_name)
        deployment = create_deployment(deployment_object)
        print("Deployment created successfully.")
    else:
        deployment = matches[0]
        print(f"Curl test deployment {deployment_name} already present.")

    match_labels_selector = utils.label_dict_to_kube_api_label_selector(deployment.spec.selector.match_labels)
    deployment_pod_response = coreV1.list_namespaced_pod(namespace, label_selector=match_labels_selector)
    pod_matches = list(deployment_pod_response.items)

    deployment_pod = pod_matches[0]
    pod_name = deployment_pod.metadata.name

    command_as_string = " ".join(exec_command)
    print(f"Exec inside {pod_name} the following curl command: {exec_command}")
    print(f"Command string: {command_as_string}")
    response = stream(coreV1.connect_get_namespaced_pod_exec, pod_name, namespace,
                  command=exec_command,
                  stderr=False, stdin=False,
                  stdout=True, tty=False)

    print("Command response: " + response)
    return response
