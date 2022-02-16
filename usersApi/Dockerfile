FROM python:3.8-slim
#ENV PYTHONUNBUFFERED 1

WORKDIR /server
COPY . /server/

RUN pip install pip --upgrade
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

RUN alambic upgrade head

EXPOSE 8000