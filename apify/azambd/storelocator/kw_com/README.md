# kw.com crawler

## How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

## Description

Please crawl https://www.kw.com/offices (1,132 in the US by counting bubbles on locator when zoomed out at max). Note: current vendor mentioned that some locations don't include city, state &/or zip. If that's the case, that's ok; just input <MISSING> in those fields.

## RND

I found `1111` stores from an internal api `https://api-endpoint.cons-prod-us-central1.kw.com/graphql` takes `4s` as of 28 Oct 2021

### MISSING FIELDS

- location_type
- hours_of_operation
- `city`, `state`, `zip_postal` are MISSING in lot of stores
