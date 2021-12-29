# How to write a Python3 scraper for SafeGraph (Simple)


Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

## Description

Please crawl arco.co.uk. We only want their own stores, not stores that carry their equipment. Included in the results, is a field that says "Arco Store" with values "Yes" or "No"; you may be able to use this as an indicator.

## Note:

- extra data field is "Arco Store"

## RND

- found 1 stores here as of 11th July 2021 

## Updated: 
- Website updated so it needed rewrite 
- Found 1 store as of 4th Nov 2021
- API endpoint https://www.arcosafety.ie/store-finder?q=&page=0&productCode=&show=All&fetchAll=true 
- Not applicable `"Acro Store" with values "Yes" or "No";` and extra data field 

