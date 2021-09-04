# How to write a Python3 scraper for SafeGraph (Simple)


Checked myself, data is valid: --ignore StreetAddressHasStateName --ignore StateLevelCountValidator

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py


## Description

Detected row count deviation: row count was 90 on 2021-07-13 and 55 on 2021-07-20 (when it was last run). Please confirm correct outcome & ensure Crawler returns that outcome.

## R&D:

- It has CloudFlare(CF) protection & must need US proxy to subdue the CF 

- Total 56 locations found as of 11 Aug 2021, although 90 locations in the past 

## Info: 
- Previous ticket info: `https://safegraph-crawl.atlassian.net/browse/SLC-16685` 
