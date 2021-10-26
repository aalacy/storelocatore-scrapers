# cookieskids.com crawler

## How to write a Python3 scraper for SafeGraph (Simple)


Checked myself, data is valid: --ignore StreetAddressHasStateName --ignore StateLevelCountValidator

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

## Description

Please crawl cookieskids.com (~6 locations)

## Info:

Locations: https://www.cookieskids.com/locations.aspx
Detected a Cloudflare version 2 Captcha challenge.

## R&D:

Takes `~a minute` to scrape `6 locations` using sgselenium 

### MISSING FIELDS

- location_type
- store_number
