FROM bitnami/odoo:16.0.20230515-debian-11-r3
COPY . /bitnami/odoo/data/addons/16.0
RUN pip3 install --upgrade pip
RUN pip3 install -r ./requirements.txt