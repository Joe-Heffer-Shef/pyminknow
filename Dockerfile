FROM python:3.7-slim-buster
MAINTAINER "Joe Heffer <j.heffer@sheffield.ac.uk>"

# Build
EXPOSE 9501

# Update system
RUN apt-get update

RUN useradd --create-home minknow
WORKDIR /home/minknow
USER minknow

RUN pip install --upgrade pip

# Install application
COPY requirements.txt .
RUN pip install -r requirements.txt --quiet

COPY pyminknow .

# Start
CMD ["python", "pyminknow", "--verbose"]
