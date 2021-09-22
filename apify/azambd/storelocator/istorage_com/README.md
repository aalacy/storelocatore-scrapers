# How to write a Python3 scraper for SafeGraph (Simple)

## Note: 

This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py




### Few Extra Notes:

> some of the locations HOO are available on `https://www.securcareselfstorage.com/`  page so these are missing as it is outside of the main domian

>It had to use '--ignore StreetAddressHasNumber' flag during validation process becase 'street_address': `5000 Farm to Market 2920 Spring` is correct with respect to source webiste page: https://www.istorage.com/storage/texas/storage-units-spring/5000-Farm-to-Market-2920-203


> Used flag: '--ignore GeoConsistencyValidator' 
Validetor caught an ERROR: 93340   CA  ZIPCODE_NOT_IN_STATE , source website page had this info: `302 Ramona Ave
Monterey, CA 93340`
website page: https://www.istorage.com/storage/california/storage-units-monterey/302-Ramona-Ave-569