FROM python:3.8-slim-buster

RUN mkdir configs/
RUN mkdir trader/
RUN mkdir strategy/
RUN mkdir logs/

ADD trader trader/
COPY structs.py ./
COPY utils.py ./
COPY strategy_runner.py ./
COPY strategy/fractals.py strategy/
COPY configs/settings.prod.ini configs/

COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD ["python","strategy_runner.py"]