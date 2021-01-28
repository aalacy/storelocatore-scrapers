FROM safegraph/apify-python3:latest

USER root

# Install openssl
RUN apt-get update \
    && apt-get install -y build-essential checkinstall libreadline-gplv2-dev libncursesw5-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev \
    && cd /usr/src \
    && curl https://www.openssl.org/source/openssl-1.1.1f.tar.gz | tar xz \
    && cd openssl-1.1.1f \
    && ./config shared --prefix=/usr/local/ \
    && make \
    && make install \
    && mkdir lib \
    && cp ./*.so ./lib \
    && cp ./*.so.1.1 ./lib \
    && cp ./*.a ./lib \
    && cp ./*.pc ./lib \
    && /sbin/ldconfig -v

COPY . ./

RUN pip3 install -r requirements.txt

RUN pip3 install certifi \
    && ln -s /usr/local/lib/python3/site-packages/certifi/cacert.pem /usr/local/ssl/cert.pem

CMD npm start
