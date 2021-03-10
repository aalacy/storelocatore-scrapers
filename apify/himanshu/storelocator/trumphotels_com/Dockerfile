FROM safegraph/apify-python3:latest

COPY . ./

USER root

RUN pip3 install -r requirements.txt

RUN google-chrome --version

CMD npm start
