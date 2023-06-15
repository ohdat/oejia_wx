FROM bitnami/odoo:16.0.20230515-debian-11-r3
COPY . /opt/bitnami/odoo/lib/odoo-16.0.post20230515-py3.10.egg/odoo/addons/
RUN pip3 install --upgrade pip
RUN pip3 install -r ./opt/bitnami/odoo/lib/odoo-16.0.post20230515-py3.10.egg/odoo/addons/requirements.txt