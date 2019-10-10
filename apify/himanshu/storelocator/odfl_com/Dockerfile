FROM safegraph/apify-python3:latest

COPY . ./

USER root

RUN python3 -V

RUN apt-get update

RUN apt-get install -y curl wget

RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

RUN apt-get install -y libdbus-glib-1-2

RUN pip3 install -r requirements.txt

RUN firefox -V

CMD npm start

