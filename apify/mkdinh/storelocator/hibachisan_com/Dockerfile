FROM safegraph/apify-python3:latest

COPY . ./

USER root

RUN pip3 install -r requirements.txt

# Install Java.
RUN \
    apt-get update && \
    apt-get install -y openjdk-8-jre && \
    rm -rf /var/lib/apt/lists/*

# Define commonly used JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64

RUN export java=usr/lib/java

CMD npm start
