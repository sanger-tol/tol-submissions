# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

FROM gitlab-registry.internal.sanger.ac.uk/tol/tol-core/api-base:1.0.0

ENV PYTHONDONTWRITEBYTECODE 1
ENV UWSGI_CHEAPER 4
ENV UWSGI_PROCESSES 64

COPY app/requirements.txt /app
COPY app/setup.py /app

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-setuptools

RUN pip3 install --upgrade setuptools
RUN python3 setup.py install

RUN pip3 --no-cache-dir install -r requirements.txt
RUN pip3 --no-cache-dir install 'connexion[swagger-ui]'

# install internal certificates
RUN pip install --upgrade certifi
COPY cacert.pem /
RUN cat /cacert.pem >> /usr/local/lib/python3.10/site-packages/certifi/cacert.pem
ENV REQUESTS_CA_BUNDLE=/usr/local/lib/python3.10/site-packages/certifi/cacert.pem

COPY ./app /app
COPY ./migrations /migrations

RUN echo "uwsgi_read_timeout 300s;" > /etc/nginx/conf.d/custom_timeout.conf
RUN echo "proxy_read_timeout 300;" >> /etc/nginx/conf.d/custom_timeout.conf
RUN echo "proxy_connect_timeout 300;" >> /etc/nginx/conf.d/custom_timeout.conf
RUN echo "proxy_send_timeout 300;" >> /etc/nginx/conf.d/custom_timeout.conf