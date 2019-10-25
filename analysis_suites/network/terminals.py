terminals = {
  "no_problem": {
    "summary": lambda args:(
      f"You got 99 problems but {args['svc_name']} ain't one. "
      f"Traffic successfully went through service -> "
      f"deployment -> pod -> image."
    ),

    "steps": lambda args: ["Have an apple."],
    "commands": lambda args: [
      'Work the business logic now'
    ],
    "resources": lambda args: []
  },

  "dns_working": {
    "summary": lambda args:
    f"{args['dns_type']}DNS is up, but the auto-generated domain name for "
    f"{args['svc_name']}, '{args['fqdn']}, still isn't working.",

    "steps": lambda args: [
      f"Kind of a mystery at this point",
      f"Make sure you read through the references below"
    ],
    "resources": lambda args: [
      {
        "name": "Debugging DNS",
        "url": "https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/"
      }
    ]
  },

  "dns_not_working": {
    "summary": lambda args:
    f"The auto-generated domain name for "
    f"{args['svc_name']}, '{args['fqdn']}, isn't working. because"
    f"there's something wrong with {args['dns_type']}DNS.",

    "steps": lambda args: [
      f"Kind of a mystery at this point",
      f"Make sure you read through the references below"
    ],
    "resources": lambda args: [
      {
        "name": "Debugging DNS",
        "url": "https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/"
      }
    ]
  },

  "dep_pod_mismatch": {
    "summary": lambda args:
    f"The service {args['svc_name']} is pointing to the wrong pods,"
    f"likely because labels/namespaces are mismatched.",

    "steps": lambda args: [
      f"Should be fairly straightforward.",
      f"You *want* the service {args['svc']} to reference "
      f"the same pods as its deployment - {args['dep_name']}",
      f"Make sure that the service's selector uses the same "
      f"labels as the deployment's spec.metadata.labels",
      f"Yes, Mosaic will be able to do this soon :)"
    ],

    "commands": lambda args: [
      f"$svc=kubectl get svc {args['svc_name']} -o json"
      f"--namespace={args['ns']}",
      f"$dep=kubectl get deployment {args['dep_name']} -o json"
      f"--namespace={args['ns']}",
      f"echo $svc | jq .spec.selector",
      f"echo $dep | jq .spec.template.metadata.labels",
    ],

    "resources": lambda args: [
      {
        "name": "Debugging DNS",
        "url": "https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/"
      },
      {
        "name": "Debugging Services",
        "url": "https://kubernetes.io/docs/tasks/debug-application-cluster/debug-service/"
      }
    ]
  },

  "pods_not_running": {
    "summary": lambda args:
    f"Very simple, the pods meant to be receiving the traffic ain't around.",

    "steps": lambda args: [
      "You have to find out why your pods aren't running",
      f"If you're lucky it's because the deployment {args['dep_name']}"
      "has replicas scaled down to 0.",
      f"Otherwise, you have to debug your pods. "
      f"Fortunately, Mosaic will have the Pod Debugger up soon!"
    ],

    "resources": lambda args: [
      {
        "name": "Debugging Pods",
        "url": "https://kubernetes.io/docs/tasks/debug-application-cluster/debug-pod-replication-controller/"
      }
    ]
  },

  "ports_configs_bad": {
    "summary": lambda args:
    f"Straightforward problem: ",

    "steps": lambda args: [
      "You have to find out why your pods aren't running",
      f"If you're lucky it's because the deployment {args['dep_name']}"
      "has replicas scaled down to 0.",
      f"Otherwise, you have to debug your pods. "
      f"Fortunately, Mosaic will have the Pod Debugger up soon!"
    ],

    "resources": lambda args: [
      {
        "name": "Debugging Pods",
        "url": "https://kubernetes.io/docs/tasks/debug-application-cluster/debug-pod-replication-controller/"
      }
    ]
  },

  "container_problem": {
    "summary": lambda args:
    f"It's looking like a port mismatch or a container problem",
    "steps": lambda args: [
      f"Try running your app without Docker (lol what is this 2010?)",
      f"If that works, run it as a Docker container",
      f"Assuming both work, make sure your svc ${args['svc_name']} uses the same targetPort you just used.",
      f"Mosaic will be able to run your docker container natively in an upcoming release :)"
    ],
    "commands": lambda args: [
      f"docker run {args['img']} -p {args['target_port']}:{args['target_port']}"
    ],
    "resources": lambda args: [
      {
        "name": "Understanding EXPOSE and targetPort",
        "url": "https://medium.com/faun/should-i-configure-the-ports-in-kubernetes-deployment-c6b3817e495"
      }
     ]
  },

  "pods_connecting": {
    "summary": lambda args:
    f"This is a tough one. If you figure it out, let me know so the app can reflect this.",
    "steps": lambda args: [
      f"Have fun on forums :)",
      f"Let me know what you find at xavier@codenectar.com"
    ],
    "commands": lambda args: [],
    "resources": lambda args: []
  }
}