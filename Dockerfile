FROM bitnami/odoo:16.0.20230515-debian-11-r3
COPY ./requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get -y update
RUN apt-get -y install git
