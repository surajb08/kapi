## Prerequisites

You will need the following things properly installed on your computer:

* [Git](http://git-scm.com/)
* [Python 3](https://www.python.org/)
* [Docker](https://www.docker.com/)

## Running

To run the project locally follow the following steps:

* change into the project directory
* `docker build -t backend-api .`
* `docker run -p 5000:5000 -v /HOST/PATH/TO/BACKEND/FOLDER:/app backend-api`


### Example endpoint calls

curl http://0.0.0.0:5000/api/namespaces
curl http://0.0.0.0:5000/api/deployments/frontend

curl "0.0.0.0:5000/api/deployments?namespace=default
curl "0.0.0.0:5000/api/deployments?namespace=default&label=app:redis"

curl 0.0.0.0:5000/api/namespaces/default/deployments
curl http://0.0.0.0:5000/api/namespaces/default/deployments/frontend
 