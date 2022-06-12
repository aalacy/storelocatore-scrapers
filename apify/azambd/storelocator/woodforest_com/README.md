# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

## Description

Detected row count deviation: row count was 713 on 2021-04-09 and 586 on 2021-04-16 (when it was last run). Please confirm correct outcome & ensure Crawler returns that outcome.

## Ran locally and Total Location Pulled = 768 as of 17th May, 2021 

> Checked myself, data is valid : --ignore StreetAddressHasStateName --ignore StreetAddressHasNumber