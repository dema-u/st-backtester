FROM python:3.8-slim-buster

COPY requirements.txt .
RUN pip install requirements.txt

COPY trader .
COPY strucs .
COPY utils .

RUN mkdir /configs
COPY configs/settings.prod.ini configs

CMD ['strategy_runner.py']
ENTRYPOINT ['python']