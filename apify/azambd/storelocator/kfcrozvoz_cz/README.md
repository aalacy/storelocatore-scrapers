# Crawl kfcrozvoz_cz

## How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

## Description

Please crawl kfcrozvoz.cz for locations in Czech republic

## Info:

- source page https://kfc.cz/main/home/restaurants
- it has internal API Endpoint: https://kfcrozvoz.cz/ordering-api/rest/v2/restaurants/ but it needs Authorization: Bearer Token
- need to check if this Authorization: Bearer is dynamic or static
- if Authorization: Bearer is dynamic then we can easily pull it by sgselenium

## R&D:

There are `107` stores as of 6th Sep 2021. Bearer token seems static. But need to check in PRE-QA.

### MISSING Fieds:

- location_type
- state
