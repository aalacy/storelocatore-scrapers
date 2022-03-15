#!/bin/bash

echo "Copying run_scraper.sh, apify_to_csv.py, csv-differ.py, validate.py to [$(pwd)/scripts]..."

mkdir scripts 2>/dev/null

cp ../../../../scripts/run_scraper.sh scripts
cp ../../../../scripts/apify_to_csv.py scripts
cp ../../../../scripts/csv-differ.py scripts
cp ../../../../scripts/validate.py scripts

chmod +x scripts/*.sh
