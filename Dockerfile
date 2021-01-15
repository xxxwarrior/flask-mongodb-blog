FROM python:3.8
ADD . /flask-app
WORKDIR /flask-app
RUN pip3 install -r requirements.txt
