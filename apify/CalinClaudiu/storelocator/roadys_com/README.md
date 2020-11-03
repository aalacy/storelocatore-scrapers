# How to write a Python3 scraper for SafeGraph (Simple)

Validator errors:

validate.py data.csv --ignore GeoConsistencyValidator --ignore FillRateValidator --ignore StreetAddressHasNumber
 
 street_address              REASON  rowNumber
82   N. 6466 4th Ct.  ADDR_HAS_NO_NUMBER         82
159     Exit 87 I-10  ADDR_HAS_NO_NUMBER        159
183    P.O. Box 7608  ADDR_HAS_NO_NUMBER        183

Website has odd data for the above fields.

FillRateValidator:

All hours are <MISSING> due to all stores being open 24/7, grabbing this info requires one extra request per store.

GeoConsistencyValidator:

Website data error https://roadys.com/location/1115/Georgetown-TX/Roadys-Walburg-Travel-Center/
Stores zip as 78686
When it should be 78626 (according to maps api in page)

←[31mFound 1 concerning rows. Examples:
       zip state                REASON  rowNumber
136  78686    TX  ZIPCODE_NOT_IN_STATE        136





Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
