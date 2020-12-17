FROM python:3.6.12-buster

RUN mkdir configs/
RUN mkdir trader/
RUN mkdir strategy/
RUN mkdir logs/
RUN mkdir utils/

ADD trader trader/
ADD utils utils/
ADD strategy strategy/
ADD configs configs/
COPY strategy_runner.py ./

COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD ["strategy_runner.py"]
ENTRYPOINT ["python"]