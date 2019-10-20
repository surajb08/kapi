copy_tree = {
  "service_connects": {
    "summary": lambda args:
    f"Let's make sure there's a problem first. Let's connect to "
    f"{args['dep_name']} from its service {args['svc_name']} "
    f"via port {args['port']}."
    ,
    "steps": lambda args: [
      f"Create/reuse a stunt pod to send a cURL from",
      f"Tell the stunt pod to cURL {args['svc_name']} on port {args['port']}"
    ],
    "commands": lambda args: [
      f"kubectl run {args['pod_name']} --image=nectar_cs/curler:latest "
      f"--namespace={args['ns']} #if not found",
      f"kubectl exec {args['pod_name']} -- curl {args['target_url']}:{args['port']} "
    ],
    "conclusion": {
      "positive": lambda args: [f"Returned status {args['status']}. Everything's working."],
      "negative": lambda args: [f"Could not connect, there is indeed a problem."]
    },
  },

  "does_svc_see_any_pods": {
    "summary": lambda args: (
      f"We're going to check whether the service {args['svc_name']} 'sees' "
      f"any pods at all."
    ),
    "steps": lambda args: [
      f"Get {args['svc_name']}'s 'endpoints' (target pod IPs)",
      f"Check if that list is empty or not"
    ],
    "commands": lambda args: [
      f"kubectl get endpoints {args['svc_name']} --namespace={args['ns']} "
    ],
    "outcome": {
      "positive": lambda args: [f"The plot thickens..."],
      "negative": lambda args: [f"Let's find out why: are your pods not running or just being found."]
    },
  },

  "does_svc_sees_right_pods": {
    "summary": lambda args: (
      f"Is the service pointing to the deployment {args['svc_name']}'s "
      f"pods or some other random pods?"
    ),
    "steps": lambda args: [
      f"Get {args['svc_name']}'s 'endpoints', i.e target podIPs",
      f"Get the IPs of all of {args['dep_name']}'s pods"
      f"Check that 100% of the returned IPs belong to the found pods"
    ],
    "commands": lambda args: [
      f"kubectl get endpoints {args['svc_name']} --namespace={args['ns']}",
      f"kubectl get pods -l {args['label_comp']} --namespace={args['ns']}"
    ],
    "outcome": {
      "positive": lambda args: [f"Big win. Now we can look at the pod level."],
      "negative": lambda args: [f"This is the problem."]
    },

    "terminals": { "negative": "deployment_pod_mismatch" }
  },

  "are_any_pods_running": {
    "summary": lambda args: (
      f"Make sure at least one of {args['dep_name']}'s pods running?"
    ),
    "steps": lambda args: [
      f"Get list of {args['dep_name']}'s pods",
      f"Count how many are in phase RUNNING"
    ],
    "commands": lambda args: [
      f"kubectl get pods -l {args['label_comp']} --namespace={args['ns']}"
    ],
    "outcome": {
      "positive": lambda args: [f"Returned status {args['status_code']}. Everything's working."],
      "negative": lambda args: [f"Could not connect, there is no problem."]
    },
  }
}