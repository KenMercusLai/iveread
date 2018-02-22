FROM python:3.5.2

WORKDIR /opt

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
