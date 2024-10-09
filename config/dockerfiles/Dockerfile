FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir /code_app
WORKDIR /code_app
COPY ./pip/requirements.txt .

RUN pip install -Ur requirements.txt

CMD ["python3", "parser.py"]