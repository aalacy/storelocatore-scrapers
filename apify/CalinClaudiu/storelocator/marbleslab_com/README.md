# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore GeoConsistencyValidator --ignore StoreNumberColumnValidator --ignore LatLngDuplicationValidator


75  29.7818762  -95.5388922  {756 Memorial City Mall,  Space 845-B, 756 Mem...          3

3 stores in same mall ↑

229  90707    TX  ZIPCODE_NOT_IN_STATE        229
Data from API, checked for errors.



Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
