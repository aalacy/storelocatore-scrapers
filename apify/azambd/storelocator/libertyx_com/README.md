# How to write a Python3 scraper for SafeGraph (Simple)


Checked myself, data is valid: --ignore StreetAddressHasStateName --ignore StateLevelCountValidator

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py


## New Crawl libertyx_com

## Description

Please crawl libertyx.com for Bitcoin ATM locations

## R&D:

- It may have CF protection

Found a `json response` => `https://libertyx.com/xhr/mobile/list_locations` 
We need to test all the zips and see the result and is there any `CF` issue I ran about 100 `zips` but did not find any issue yet

- I wrote script to pull all locations, but you may filter Bitcoin ATM locations from results. 
