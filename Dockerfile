FROM python:3.7-slim-buster

EXPOSE 9501

RUN apt-get update
RUN pip install --upgrade pip

RUN useradd minknow --create-home
WORKDIR /home/minknow

USER minknow

COPY requirements.txt .
RUN pip install -r requirements.txt --user

COPY pyminknow pyminknow

LABEL maintainer="Joe Heffer <j.heffer@sheffield.ac.uk>" \
version=1.0.0

CMD ["python", "pyminknow", "--verbose"]
