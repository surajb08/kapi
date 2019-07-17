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