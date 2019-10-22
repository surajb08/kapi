copy_tree = {
  "does_svc_connect": {
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
      "positive": lambda args: [f"The Service -> Pod -> Container -> App chain is working."],
      "negative": lambda args: [f"Could not connect, there is indeed a problem."]
    },
  },

  "is_svc_visible": {
    "summary": lambda args:
    f"We're going to check if the cluster's DNS can resolve ${args['svc_name']}'s "
    f"partially qualified domain name - ${args['fqdn']}."
    ,
    "steps": lambda args: [
      f"Run nslookup against ${args['svc_name']} from inside the cluster",
      f"Check that there is an entry for ${args['fqdn']}"
    ],
    "commands": lambda args: [
      f"kubectl run {args['pod_name']} --image=nectar_cs/curler:latest "
      f"--namespace={args['ns']}",
      f"kubectl exec {args['pod_name']} nslookup {args['fqdn']}"
    ],
    "conclusion": {
      "positive": lambda args: [
        f"The cluster's DNS is working, huge relief.",
        f"This means {args['fqdn']} -> {args['svc_ip']} is happening correctly."
      ],
      "negative": lambda args: [f"Problem identified. Open the Solutions page."]
    },
  },

  "does_svc_see_pods": {
    "summary": lambda args: (
      f"We're going to check whether the service {args['svc_name']} 'sees' "
      f"any pods at all, where it's meant to forward traffic to."
    ),
    "steps": lambda args: [
      f"Get {args['svc_name']}'s 'endpoints' (target pod IPs)",
      f"Check if that list is empty or not"
    ],
    "commands": lambda args: [
      f"kubectl get endpoints {args['svc_name']} --namespace={args['ns']} "
    ],
    "conclusion": {
      "positive": lambda args: [
        f"{args['svc_name']} knows to forward traffic to {args['ep_count']} pods.",
        f"Next, we're going to check if those are the right pods"
      ],
      "negative": lambda args: [
        f"Things are failing because {args['svc_name']} isn't forwarding traffic anywhere.",
        f"Let's find out why."
      ]
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
    "conclusion": {
      "positive": lambda args: [
        f"Big win. Now we can look at the pod level."
      ],
      "negative": lambda args: [
        f"This is the problem."
      ]
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
    "conclusion": {
      "positive": lambda args: [f"Returned status {args['status_code']}. Everything's working."],
      "negative": lambda args: [f"Could not connect, there is no problem."]
    },
  }
}