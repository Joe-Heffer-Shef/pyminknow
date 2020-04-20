FROM python:slim-buster
MAINTAINER "Joe Heffer <j.heffer@sheffield.ac.uk>"

# Build
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 9501

# Start
CMD ["python", "pyminknow", "--verbose"]
