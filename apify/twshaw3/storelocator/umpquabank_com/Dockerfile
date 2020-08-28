FROM safegraph/apify-python3-stdout:latest

COPY . ./

USER root

RUN pip3 install -r requirements.txt

CMD npm start
