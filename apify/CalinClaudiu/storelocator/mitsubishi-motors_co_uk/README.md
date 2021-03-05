# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore StoreNumberColumnValidator --ignore CountryCodeFillRateChecker

Throws one duplicate, which is not a duplicate but just entered twice in their locator.. it has unique ID for each entry:
gb_en_1602841767331
gb_en_1602844049876
but all other data is the same.

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
