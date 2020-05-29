  
FROM safegraph/apify-python3-chromedriver-upgrade:latest

COPY . ./

USER root

RUN pip3 install -r requirements.txt

CMD npm start
