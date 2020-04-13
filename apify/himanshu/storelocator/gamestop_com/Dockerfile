FROM safegraph/apify-python3:latest

COPY . ./

USER root

RUN pip3 install -r requirements.txt

# CMD export SSL_CERT_FILE=/charles-ssl-proxying-certificate.pem && npm start
CMD npm start
