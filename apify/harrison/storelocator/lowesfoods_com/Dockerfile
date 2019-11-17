FROM node:10-alpine

COPY . ./

RUN npm --quiet set progress=false \
 && npm install --only=prod --no-optional \
 && echo "Installed NPM packages:" \
 && npm list \
 && echo "Node.js version:" \
 && node --version \
 && echo "NPM version:" \
 && npm --version

USER root

ENV NODE_ENV=production
ENV NODE_OPTIONS="--max_old_space_size=30000"

CMD npm start
