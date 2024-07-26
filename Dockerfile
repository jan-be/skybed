FROM python:3.12-alpine

RUN pip install numpy docker

COPY . .

CMD python uas_pilot.py
