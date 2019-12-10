FROM safegraph/apify-node:latest

COPY . ./

RUN npm install

CMD npm start && ./check_output.sh
