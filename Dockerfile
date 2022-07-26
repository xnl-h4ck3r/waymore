FROM python:3.10


WORKDIR /app

COPY . . 

RUN mkdir -p results

RUN python3 setup.py install

