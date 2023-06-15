FROM FROM python:3.9
RUN mkdir /dist
WORKDIR /dist
COPY . .
RUN pip3 install --upgrade pip
RUN pip3 install -r ./opt/bitnami/odoo/lib/odoo-16.0.post20230515-py3.10.egg/odoo/addons/requirements.txt