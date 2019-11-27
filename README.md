# Kapi = K8Kat and Backend

Kapi - pronounced *Kapee* - acts as the local backend for the [Nectar MOSAIC](https://github.com/nectar-cs/mosaic) web application.

It is composed of two parts that  will soon be broken up: K8Kat and the backend. 

K8Kat will shortly published as a standalone Python3 lib. 

# K8Kat

K8Kat is a Python 3 (soon to be standalone) library for interfacing with Kubernetes. It is built **on top of the official [kubernetes-client/python](https://github.com/kubernetes-client/python)**.

It lets you query, inspect, and manipulate Kubernetes objects with a fraction of the kung-fu required in the official lib or  `kubectl X | jq Y`.

Think Ruby's ActiveRecord for a cluster.

## TLDR

### Playing with Deployments
```python
alpha_deps = K8Kat.deps().ns("default", "nectar").lbs_inc_any(v='alpha')

for dep in alpha_deps: 
   for pod in dep.pods():
      pod.wait_until(status="Running")      
      pod.cmd("rake db:migrate")
   dep.set_label(v='beta')
   dep.scale(by=1)

```


### Debugging Bad Pods
```python
bad_pods = K8kat.deps().not_ns("dev").find("nlp-main").pods().broken() 

bad_pods.pretty_pluck("ns", "status", "image")
# [<nlp-main-8689d59f49-x74qd: production | CrashLoopBackoff | hooli/nlp_main:latest>]

bad_pods[0].logs(3600)

bad_pods[0].explain_error()
```


### Debugging Bad Services
```python
problem_svc = K8kat.svcs().ns('default').find('my-svc')
curler = CurlPod(target=target_svc.fqdn, ns='default')
curler.curl('/api') # -> None

problem_svc.pods() #to check if selectors working

problem_svc.raw_endpoints() # see if any

problem_svc.endpoint_ips # or use sugar method
# ['10.56.0.239']

dns_pods = K8Kat.pods().system().lbs_inc_each(app='kube-dns')
dns_pods.pretty_pluck('status')
# [<kube-dns-67947d6c68-5dvn4: Running | docker.io/nlp_main:latest>]

suspect = "failed" in dns_pods[0].logs()

curler.delete()
```


### Querying
K8Kat queries dynamically decide which parts of the query should be done by Kubernetes, versus which must be done with its own logic. You can therefore combine traditional filters like `labels` with K8Kat attributes like `status`, not caring about *how* the query gets executed.

The logic inside K8Kat queries is essentially:

```python
query = query.exec_as_much_as_possible_with_k8s_api()
query = query.do_the_rest_locally()
return query
```

### Inspecting
Raw Kubernetes resources are wrapped in the KatRes to deliver all kinds of sugar. This ranges from basic properties that are normally nested neep in JSON (e.g `service.status.load_balancer.ingress[n].ip`), to computations that would require more logic, e.g `pod.explain_error()`.


### Manipulating
Using the wrapper described above, cluster-state-changing operations are also made faster, notably scaling, deleting, annotating, sending commands, and labelling.


## Getting Started
Until it is moved to its own repo and package-ized, there's no reasonable way to integrate the source :/

To *test drive* K8Kat though, you can access the API through the Flask app. Assuming you're running MOSAIC, you can:
```shell
pod=$(k get pod -l app=kapi -o json -n nectar | jq .items[0].metadata.name -r)
k exec -it pods/$pod -c main -n nectar -- /bin/bash
flask shell
```

Note that **K8Kat is in pre-alpha**. It does just enough to serve MOSAIC but it was built extremely hastily and is poorly architected. Follow the project to know when it's ready for IRL usage.

Better yet though, come help build it:

## Getting Involved

We're looking for cream of the crop engineers who want to create the new standard in container orchestration for the next decade.

Frontend, backend, infra, design, VP Developer Advocacy, and CTO. London, San Francisco, or remote. Drop me a line.

Drop me a line at xavier@codenectar.com or on the K8s slack.

# Backend

It's a backend built with Flask.
