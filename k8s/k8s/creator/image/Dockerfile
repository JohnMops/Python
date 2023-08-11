FROM python:3.11
ADD . /src
RUN pip3 install kopf
RUN pip3 install -r requirements.txt
CMD kopf run -A --log-format=full  /src/main.py -A