FROM python:3.12

WORKDIR /server

COPY . .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

CMD ["python3", "server_with_logs.py"]