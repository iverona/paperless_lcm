# syntax=docker/dockerfile:1

FROM python:3-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY lcm.py .

CMD [ "python3", "lcm.py"]
