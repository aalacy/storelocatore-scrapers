# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

## Description

Please crawl vans.com & include all locations globally except UK, EU & AUS. Because UK&EU has different API Endpoints and AUS has other API Endpoints. 

## Info: 
AUS Ticket: https://safegraph-crawl.atlassian.net/browse/SLC-32345
UK&EU Ticket: https://safegraph-crawl.atlassian.net/browse/SLC-32346