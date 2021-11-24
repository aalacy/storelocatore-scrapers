#!/bin/bash

# Runs the scraper in the local env and docker, and compares outputs.
#

SG_HOME="${1}"
SCRAPE_DIR="${2}"
EXTRA_INFO="${3}"

DIR="$SG_HOME/apify/$SCRAPE_DIR"
LOGFILE="$SG_HOME/crawl-diff.log"

(
  cd "$DIR" && \
  cp -f "$SG_HOME/scripts/run_scraper.sh" . && \
  chmod +x run_scraper.sh && \
  cp -f "$SG_HOME/scripts/apify_to_csv.py" . && \
  cp -f "$SG_HOME/scripts/csv-differ.py" . && \
  START=$SECONDS && \
  python scrape.py && \
  LOCAL_TIME=$((SECONDS-START)) && \
  mv data.csv data-local.csv && \
  START=$SECONDS && \
  ./run_scraper.sh && \
  DOCKER_TIME=$((SECONDS-START)) && \
  python apify_to_csv.py apify_docker_storage && \
  mv data.csv data-docker.csv && \
  echo "Testing: $SCRAPE_DIR" >> "$LOGFILE" && \
  echo "Local took: $LOCAL_TIME seconds. Docker run took: $DOCKER_TIME seconds. Extra info: $EXTRA_INFO" >> "$LOGFILE" && \
  python csv-differ.py data-local.csv data-docker.csv store_number >> "$LOGFILE" && \
  echo "-----------------------------------------------------------------------------------------------------" >> "$LOGFILE"
  # sudo rm -rf run_scraper.sh apify_to_csv.py csv-differ.py data-new.csv data-docker.csv data-local.csv apify_docker_storage
)
