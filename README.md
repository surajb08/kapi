# K8Kat + Backend

K8Kat will shortly published as a standalone library for Python. The need to scale Kubernetes resource ops came late in the MOSAIC project, so K8Kat didn't get built until just recently, which is why there hasn't been time to make it its own proper lib.

# K8Kat

K8Kat is a Python 3 (soon to be standalone) library for interfacing with Kubernetes. It is built **on top of the official [kubernetes-client/python](https://github.com/kubernetes-client/python)**.

It lets you query, inspect, and manipulate Kubernetes objects with a fraction of the code you would need using the official library or `kubectl X | jq Y`. 

### Querying
K8Kat has an extensible querying layer that that decides what parts of the query should be done by Kubernetes, versus which must be done in memory. This means you can combine traditional filters like `labels` with K8Kat attributes like `status`.  


Falling back to the official lib is easy though: `k8kat_res.raw`.

## TLDR
```

#-------Simple Deplyments Work------

alpha_deps = K8Kat.deps().ns("default", "nectar").lbs_inc_any(v='alpha',alpha=True)

alpha_deps.tag_each(v='stable',alpha=False)

for dep in alpha_deps:
   dep.scale(by=5)
   
   for pod in dep.pods():
      pod.wait_until(status="Running")      
      pod.cmd("rake db:migrate")
   

#-------Pod Troubleshooting ------

bad_pods = K8kat.deps().not_ns("dev").find("nlp-main").pods().broken() 

bad_pods.pretty_pluck("ns", "status", "image")
# [<nlp-main-8689d59f49-x74qd: production | CrashLoopBackoff | docker.io/nlp_main:latest>]


bad_pods[0].logs(3600)




```

## Motivation & Direction

To make the most of cloud nativity, we have need a wayyyyyyy more casual relationship with orchestrators' primitives.


# Backend

It's a backend.
