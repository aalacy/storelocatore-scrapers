# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore GeoConsistencyValidator --ignore StoreNumberColumnValidator


--ignore GeoConsistencyValidator
       zip state                REASON  rowNumber
215  46544    MI  ZIPCODE_NOT_IN_STATE        215
==Only them to blame:
https://www.cellphonerepair.com/mishawaka-mi/



--ignore StoreNumberColumnValidator
Store number column is only partially filled. Please make sure you're capturing store numbers for all POI on the store locator
==Some stores do not have a store ID and therfore no hours data.



Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
