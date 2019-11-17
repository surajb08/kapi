# Kapi = K8Kat and Backend

Kapi - pronounced *Kapee* - acts as the local backend for the [Nectar MOSAIC](https://github.com/nectar-cs/mosaic) web application.

It is composed of two parts that  will soon be broken up: K8Kat and the backend. 

K8Kat will shortly published as a standalone Python3 lib. 

# K8Kat

K8Kat is a Python 3 (soon to be standalone) library for interfacing with Kubernetes. It is built **on top of the official [kubernetes-client/python](https://github.com/kubernetes-client/python)**.

It lets you query, inspect, and manipulate Kubernetes objects with a fraction of the code you would need using the official library, TF/Pulumi, or `kubectl X | jq Y`. 

K8Kat is obviously not not exhaustive - that's what the official lib is for - but it should help DRY things up and hopefully encourage you to grab your cluster by the horns (see Motivation).

## TLDR
```python

alpha_deps = K8Kat.deps().ns("default", "nectar").lbs_inc_any(v='alpha',alpha=True)

for dep in alpha_deps:
   dep.set_label(v='beta', alpha=False)
   dep.scale(by=1)
   
   for pod in dep.pods():
      pod.wait_until(status="Running")      
      pod.cmd("rake db:migrate")
```

```python
   

#-------Pod Troubleshooting ------

bad_pods = K8kat.deps().not_ns("dev").find("nlp-main").pods().broken() 

bad_pods.pretty_pluck("ns", "status", "image")
# [<nlp-main-8689d59f49-x74qd: production | CrashLoopBackoff | docker.io/nlp_main:latest>]

bad_pods[0].logs(3600)

bad_pods[0].epxplain_error()
```

### Querying
K8Kat queries dynamically decide which parts of the query should be done by Kubernetes, versus which must be done with its own logic. You can therefore combine traditional filters like `labels` with K8Kat attributes like `status`, not caring about *how* the query gets executed.

### Inspecting
Raw Kubernetes resources are wrapped in the KatRes to deliver all kinds of sugar. This ranges from basic properties that are normally nested neep in JSON (e.g `service.status.load_balancer.ingress[n].ip`), to computations that would require more logic, e.g `pod.explain_error()`.

### Manipulating
Using the wrapper described above, cluster-state-changing operations are also made faster, notably scaling, deleting, annotating, sending commands, and labelling.

## Motivation

To make the most of cloud nativity, we have need a wayyyyyyy more casual relationship with orchestrators' primitives.

If it took 3 lines plus a test to serve JSON on the web, there wouldn't be as many APIs around today.

Hopefully, this moves us closer to properly programmable infrastructure.

## Getting Started



# Backend

It's a backend built with Flask.
