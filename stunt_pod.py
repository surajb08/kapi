from kube_apis import coreV1, client, extensionsV1Beta
import time
from pprint import pprint
from kubernetes.stream import stream


def create():
    pod = client.V1Pod(
        api_version='v1',
        metadata=client.V1ObjectMeta(
            name="nectar-stuntpod",
            labels={"yolo": "forever"}
        ),
        spec=client.V1PodSpec(
            containers=[
                client.V1Container(
                    name="nectar-stuntpod-img",
                    image="byrnedo/alpine-curl",
                )
            ]
        )
    )

    return coreV1.create_namespaced_pod(
        body=pod,
        namespace="default"
    )


def find():
    response = coreV1.list_namespaced_pod(
        'default',
        field_selector='metadata.name=nectar-stuntpod'
    )
    return response.items[0]


def wait_until_running():
    run_state = None
    for attempts in range(0, 3):
        pod = find()
        state = pod.status.container_statuses[0].state
        run_state = state.running
        if run_state is not None:
            break
        else:
            time.sleep(1)
            pprint(state)
            attempts += 1
    return run_state is not None


def run_cmd(cmd):
    return stream(
        coreV1.connect_get_namespaced_pod_exec,
        "nectar-stuntpod",
        "default",
        command=cmd,
        stderr=False,
        stdin=False,
        stdout=True,
        tty=False
    )

create()
if wait_until_running():
    print(run_cmd(['curl', "10.0.31.65:3000"]))
    coreV1.delete_namespaced_pod(
        name="nectar-stuntpod",
        namespace="default"
    )
