FROM safegraph/apify-python3-ssl-upgrade:latest

COPY . ./

USER root

RUN pip3.7 install -r requirements.txt

CMD npm start
