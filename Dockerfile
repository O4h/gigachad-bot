FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get -y update && apt-get -y install git
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "main.py"]
