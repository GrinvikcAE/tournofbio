FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /tournofbio_app
WORKDIR /tournofbio_app

RUN apt-get update \
  && apt-get -y install postgresql \
  && apt-get clean

RUN python3 -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8000

COPY . .

RUN alembic init alembic

RUN alembic upgrade head

#CMD gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:10000 --timeout 90
CMD uvicorn main:app --host 0.0.0.0 --port 8000
