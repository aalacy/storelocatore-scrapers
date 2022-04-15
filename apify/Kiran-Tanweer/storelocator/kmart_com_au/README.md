# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py


## Info:

Crawl Store Locator URL
https://www.kmart.com.au/store-locator

Website is using POST method at this API https://www.kmart.com.au/webapp/wcs/stores/servlet/AjaxStoreLocatorMapResultsView

`<script async type="text/javascript" src="/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3&ns=1&cb=1100771476"></script>`

Incapsula Triggered

## R&D

Its a complex project. I had to use `site-map`. On test I pulled 50 stores in about `15 mins`. So added `CrawlStateSingleton`. But need to be tested in production. May have `cloudflare` issues

### MISSING FIELDS

- store_number
- location_type