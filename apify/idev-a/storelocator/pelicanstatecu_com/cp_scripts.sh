#!/bin/bash

echo "Copying run_scraper.sh, apify_to_csv.py, csv-differ.py, validate.py to the current directory."

cp ../../../../scripts/run_scraper.sh .
cp ../../../../scripts/apify_to_csv.py .
cp ../../../../scripts/csv-differ.py .
cp ../../../../scripts/validate.py .

chmod +x scripts/*.sh
