FROM safegraph/apify-node:latest

COPY . ./

RUN npm install

CMD npm start && ls -al && ./check_output.sh
