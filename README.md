## Prerequisites

You will need the following things properly installed on your computer:

* [Git](http://git-scm.com/)
* [Python 3](https://www.python.org/)
* [Docker](https://www.docker.com/)
* [GCloud SDK](https://cloud.google.com/sdk/)
    * Run gcloud init
    * Connect with your gmail account
    * Select "codenectarproject", and "sample-cluster"
    * Run:'gcloud container clusters get-credentials sample-cluster --project codenectar --region us-central1-a'
    

## Running

To run the project locally follow the following steps:

* change into the project directory
* `docker build -t backend-api .`
* `docker run -p 5000:5000 -v /HOST/PATH/TO/BACKEND/FOLDER:/app backend-api`


### Example endpoint calls
```
curl http://0.0.0.0:5000/api/namespaces

curl http://0.0.0.0:5000/api/deployments/frontend

curl "0.0.0.0:5000/api/deployments?namespace=default

curl 0.0.0.0:5000/api/namespaces/default/deployments

curl 0.0.0.0:5000/api/namespaces/weave/deployments

curl http://0.0.0.0:5000/api/namespaces/default/deployments/frontend


curl "0.0.0.0:5000/api/deployments?namespace=weave&namespace=default"

curl "0.0.0.0:5000/api/deployments?label=role:master&label=role:slave&label=tier:frontend"

curl "0.0.0.0:5000/api/deployments?label=app:redis"

curl "0.0.0.0:5000/api/deployments?label=app:guestbook&label=tier:frontend"

# next one throws a 400 for malformed input
curl "0.0.0.0:5000/api/deployments?label=app:guestbook&label=tierfrontend"

# run a command inside pod
curl --header "Content-Type: application/json" -X "POST" --data '{"command": "ls -la"}' 0.0.0.0:5000/api/namespaces/default/pods/frontend-654c699bc8-fnshk/run_cmd

 
 # run a curl command from the test-pod
 curl --header "Content-Type: application/json" -X "POST" --data '{"method": "GET", "path": "/guestbook.php?cmd=get&key=messages", "headers": {}, "body": null }'  0.0.0.0:5000/api/namespaces/default/deployments/frontend/http_request
```

 