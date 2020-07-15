FROM python:3.6

ADD ./ /opt/gstore
WORKDIR /opt/gstore

RUN chmod +x bin/manage \
  && pip install -r requirements/app.txt

CMD bin/manage start --daemon-off
