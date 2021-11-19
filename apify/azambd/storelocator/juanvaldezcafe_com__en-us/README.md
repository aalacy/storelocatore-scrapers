# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

Checked myself, data was valid, SUCCESS File was not possible because <lat, lngs> with multiple addressess

## Requirements: 
Please crawl juanvaldezcafe.com/en-us. (Note: unlike most crawls where we tell you to only include US, CA & UK countries, we'd like for you to include all countries, as they are all available on the locator). SgPostal should do a pretty good job of handling parsing of addresses for the countries; but let us know if not.

## Approach: 

- Found an internal API Endpoint
- Pull Data from API: `https://storerocket.global.ssl.fastly.net/api/user/OdJEDYo4WE/locations`

## R&D: 
- previous internal API Endpoint was unavailable 
- New API Enpoint: `https://api.storerocket.io/api/user/OdJEDYo4WE/locations`

### Results: 
Total Locations:  374 as of August 11, 2021
