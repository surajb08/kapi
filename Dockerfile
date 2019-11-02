FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev docker.io \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

ADD . /app

WORKDIR /app

ARG REVISION
ENV REVISION=$REVISION

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
RUN pip3 install -r requirements.txt
EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0"]