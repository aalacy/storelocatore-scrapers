FROM node:10-slim

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y wget --no-install-recommends \
 && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
 && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
 && DEBIAN_FRONTEND=noninteractive apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y procps unzip git google-chrome-stable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst ttf-freefont \
    --no-install-recommends \
 && curl -sS http://chromedriver.storage.googleapis.com/2.46/chromedriver_linux64.zip > /tmp.zip \
 && unzip tmp.zip \
 && rm tmp.zip \
 && mv /chromedriver /bin \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /src/*.deb \
 && DEBIAN_FRONTEND=noninteractive apt-get purge --auto-remove -y curl unzip \
 && rm -rf /opt/yarn /usr/local/bin/yarn /usr/local/bin/yarnpkg

#USER root

COPY . ./

# Sets path to Chrome executable, this is used by Apify.launchPuppeteer()
ENV APIFY_CHROME_EXECUTABLE_PATH=/usr/bin/google-chrome

# Tell Node.js this is a production environemnt
ENV NODE_ENV=production

# Enable Node.js process to use a lot of memory (actor has limit of 32GB)
ENV NODE_OPTIONS="--max_old_space_size=30000"

# Install default dependencies, print versions of everything
RUN npm --quiet set progress=false \
 && npm install --only=prod --no-optional --no-package-lock \
 && echo "Installed NPM packages:" \
 && npm list || true \
 && echo "Node.js version:" \
 && node --version \
 && echo "NPM version:" \
 && npm --version \
 && echo "Google Chrome version:" \
 && bash -c "$APIFY_CHROME_EXECUTABLE_PATH --version" \
 && echo "ChromeDriver version:" \
 && chromedriver --version

CMD npm start
