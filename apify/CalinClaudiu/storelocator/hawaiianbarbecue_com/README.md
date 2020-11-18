# How to write a Python3 scraper for SafeGraph (Simple)


validate.py data.csv --ignore StreetAddressHasNumber --ignore StreetAddressHasStateName --ignore GeoConsistencyValidator --ignore CountryValidator




29          81-6602 Mamalahoa Hwy. (KTA Super Stores)  ADDR_HAS_NO_NUMBER         29
32  1255 5th St. Bldg. 1255 (Marine Corps Base Haw...  ADDR_HAS_NO_NUMBER         32
48  World Udagawacho Biru 1F,  36-6 Udagawa-cho,  ...  ADDR_HAS_NO_NUMBER         48
80            94-780 Meheula Pkwy.,  (next to Safeway)  ADDR_CONTAINS_STATE_NAME         80
101  99-115 Aiea Heights Dr.,  Ste. 145 (next to St...  ADDR_CONTAINS_STATE_NAME        101
48  150-0042  Japan  ZIPCODE_NOT_IN_STATE         48 (lol)
48  Japan  03-3463-0141  150-0042  INVALID_US_ZIP         48

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
