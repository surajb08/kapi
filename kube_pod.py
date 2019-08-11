import urllib3

import utils
from kube_apis import coreV1, extensionsV1Beta, client
from kubernetes import watch


def get_event_data_form_container_state(container_state):
    state = None
    if container_state.running is not None:
        return None

    if container_state.waiting is not None:
        state = container_state.waiting
        return {
            "reason": state.reason,
            "msg": state.message
        }

    if container_state.terminated is not None:
        state = container_state.terminated
        return {
            "reason": state.reason,
            "msg": state.message
        }

    return None

MAX_EVENT_COUNT = 10

def get_pod_events(namespace, pod_name):
    formatted_events = []
    w = watch.Watch()
    count = MAX_EVENT_COUNT
    TIMEOUT_WAITING_FOR_EVENTS = 3

    try:
        for event in w.stream(coreV1.list_namespaced_pod, namespace=namespace, field_selector=f'metadata.name={pod_name}',
                              _request_timeout=TIMEOUT_WAITING_FOR_EVENTS):
            print("Event: %s %s" % (event['type'], event['object'].metadata.name))

            state = event["object"].status.container_statuses[0].state

            formatted_event = get_event_data_form_container_state(state)
            if formatted_event is not None:
                formatted_events.append(formatted_event)

            print(formatted_event)
            count -= 1
            if not count:
                w.stop()
    except urllib3.exceptions.ReadTimeoutError:
        print(f"Waited for {TIMEOUT_WAITING_FOR_EVENTS} s for events. Moving on.")

    return formatted_events

def get_deployment_pods(deployment):
    returned_pods = []
    if deployment.spec.selector.match_labels is not None:
        match_labels_selector = utils.label_dict_to_kube_api_label_selector(deployment.spec.selector.match_labels)
        returned_pods = coreV1.list_pod_for_all_namespaces(label_selector=match_labels_selector)

    pods = []
    for returned_pod in returned_pods.items:
        pod_status = returned_pod.status.phase.upper()

        restarts = None
        age = None
        if returned_pod.status.container_statuses is not None and len(returned_pod.status.container_statuses) > 0:
            first_container = returned_pod.status.container_statuses[0]
            restarts = first_container.restart_count
            age = first_container.restart_count

        pod_namespace = returned_pod.metadata.namespace
        pod_name = returned_pod.metadata.name
        events = get_pod_events(pod_namespace, pod_name)

        pods.append({
            "name": returned_pod.metadata.name,
            "status": pod_status,
            # "container_status": WAITING | RUNNING | TERMINATED,
            "events": events,
            "restarts": restarts,
            "age": age,
        })
    return pods