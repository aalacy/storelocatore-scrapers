# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py


## Crawl princetonreview_com

## Description

Please crawl princetonreview.com for office locations per the locator url. Include all locations globallly including US, CA & international. International available from https://www.princetonreview.com/international/locations

## R&D:

- US& CA: https://www.princetonreview.com/locations
- https://www.princetonreview.com/international/locations

bad & unstructured  html tagging for the website. Total `103` stores in about `20s`

Among them `34` from base location [US,CA] and rest are from internationals.

MISSING ATTRIBUTEs:

- store_number
- location_type
- latitude
- longitude

- `hoo` Missing in international
- some address and phone also missing in international
