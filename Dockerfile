FROM bitnami/odoo:13.0.20221010-debian-11-r5
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
RUN apt-get -y update
RUN apt-get -y install git
EXPOSE 3000 8069 8072

USER root
ENTRYPOINT [ "/opt/bitnami/scripts/odoo/entrypoint.sh" ]
CMD [ "/opt/bitnami/scripts/odoo/run.sh" ]
