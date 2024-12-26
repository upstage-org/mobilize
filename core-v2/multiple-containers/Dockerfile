FROM registry.access.redhat.com/ubi9/python-312:latest

WORKDIR /usr/app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install Pillow && pip install -r requirements.txt


ADD . .
USER root
RUN chmod +x ./startup.sh

EXPOSE 3000
CMD ["/bin/bash","-c","./startup.sh"] 