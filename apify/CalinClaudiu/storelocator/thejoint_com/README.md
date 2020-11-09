# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore StreetAddressHasStateName --ignore GeoConsistencyValidator



238  6770 Veteran's Parkway, Space L  ADDR_CONTAINS_STATE_NAME        238
446  27203    TN  ZIPCODE_NOT_IN_STATE        446


446  27203   Tennessee  ZIPCODE_NOT_IN_STATE        446
595  98007  Washington  ZIPCODE_NOT_IN_STATE        595
596  98021  Washington  ZIPCODE_NOT_IN_STATE        596
597  98036  Washington  ZIPCODE_NOT_IN_STATE        597
598  98275  Washington  ZIPCODE_NOT_IN_STATE        598

595  Washington  (425) 276-7596  98007  INVALID_US_STATE        595
596  Washington  (425) 399-5044  98021  INVALID_US_STATE        596
597  Washington  (425) 549-9740  98036  INVALID_US_STATE        597
598  Washington  (425) 230-4087  98275  INVALID_US_S	TATE        598
599  Washington  (425) 287-5570  98052  INVALID_US_STATE        599


Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
