FROM safegraph/apify-python3:3.7.0

COPY . ./

USER root

RUN pip3 install -r requirements.txt

RUN google-chrome --version

CMD npm start
