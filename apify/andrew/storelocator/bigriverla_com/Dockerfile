# Dockerfile contains instructions how to build a Docker image that will contain
# all the code and configuration needed to run your actor. For a full
# Dockerfile reference, see https://docs.docker.com/engine/reference/builder/

# First, specify the base Docker image. Apify provides the following base images
# for your convenience:
#  apify/actor-node-basic (Node.js 10 on Alpine Linux, small and fast image)
#  apify/actor-node-chrome (Node.js 10 + Chrome on Debian)
#  apify/actor-node-chrome-xvfb (Node.js 10 + Chrome + Xvfb on Debian)
# For more information, see https://apify.com/docs/actor#base-images
# Note that you can use any other image from Docker Hub.
FROM node:10

# Copy all files and directories with the source code
COPY . ./

# Install NPM packages, skip optional and development dependencies to keep the
# image small. Avoid logging to much and print the dependency tree for debugging
RUN npm --quiet set progress=false \
 && npm install --only=prod --no-optional \
 && echo "Installed NPM packages:" \
 && npm list \
 && echo "Node.js version:" \
 && node --version \
 && echo "NPM version:" \
 && npm --version

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

RUN echo "ChromeDriver version:" \
 && chromedriver --version

RUN apt update && apt upgrade -y \
 && apt install build-essential -y \
 && apt install libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev -y \
 && apt install zlib1g -y \
 && wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz \
 && tar -xzvf Python-3.7.0.tgz \
 && cd Python-3.7.0 \
 && ./configure \
 && make && make install

RUN pip3 install -r requirements.txt

RUN echo "Python3 version:" \
  && python3 --version

RUN echo "PATH:" \
  && echo $PATH

# Specify how to run the source code
CMD npm start
