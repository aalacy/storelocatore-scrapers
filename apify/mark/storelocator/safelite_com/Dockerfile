FROM safegraph/apify-node:latest

COPY . ./

USER root

RUN apt-get update -y \
    && apt-get install build-essential -y \
    && apt-get install python3 -y

RUN npm install

CMD node main.js
