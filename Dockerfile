FROM python:3.11
ENV PYTHONUNBUFFERED=1
RUN mkdir /razor_app
WORKDIR /razor_app
ADD . /razor_app/
RUN pip install -r requirements.txt