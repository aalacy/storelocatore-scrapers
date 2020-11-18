# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore StreetAddressHasNumber --ignore GeoConsistencyValidator

51   West Second Avenue  ADDR_HAS_NO_NUMBER         51
77        RT. 97 (17 B)  ADDR_HAS_NO_NUMBER         77
135            Route 61  ADDR_HAS_NO_NUMBER        135
190                MILL  ADDR_HAS_NO_NUMBER        190
192      South Eight St  ADDR_HAS_NO_NUMBER        192
Above data scraped correctly.

72  01926    MA  ZIPCODE_NOT_IN_STATE         72
Above data scraped correctly.

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
