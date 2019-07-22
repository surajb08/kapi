FROM ubuntu:16.04

RUN apt-get update \
    && apt-get install -yq --no-install-recommends \
    python3 \
    python3-pip \
    curl

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin

RUN pip3 install --upgrade pip==9.0.3 \
    && pip3 install setuptools \
    && pip3 install kubernetes

EXPOSE 5000
ADD . /app

#SECURITY DISASTER REMOVE ASAP (or when running non-docker or on K8s)
RUN /app/hope.sh
WORKDIR /app
RUN pip3 install -r requirements.txt
CMD python3 app.py
