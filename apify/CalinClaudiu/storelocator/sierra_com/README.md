# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore StreetAddressHasStateName

7            2948 Golf Rd, The Shoppes at Nagawaukee  ADDR_CONTAINS_STATE_NAME         27
7   6376 Promenade Parkway, Promenade at Castle Rock  ADDR_CONTAINS_STATE_NAME         37
0  11467 Pacific Crest Place NW, The Trails at Si...  ADDR_CONTAINS_STATE_NAME         40
data from API

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
