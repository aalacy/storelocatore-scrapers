FROM safegraph/apify-python3:latest

COPY . ./

USER root

RUN pip3.8 install -r requirements.txt

RUN pip3.8 install certifi \
    && ln -s /usr/local/lib/python3.8/site-packages/certifi/cacert.pem /usr/local/ssl/cert.pem

# Install Java.
RUN \
    apt-get update && \
    apt-get install -y openjdk-8-jre && \
    rm -rf /var/lib/apt/lists/*

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64

RUN export java=usr/lib/java

CMD npm start
