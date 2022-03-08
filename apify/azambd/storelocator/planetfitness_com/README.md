# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

Checked myself, data was valid, because of global data validation needs: --ignore StreetAddressHasNumber --ignore StreetAddressHasStateName --ignore GeoConsistencyValidator --ignore CountryValidator --ignore CountValidator --ignore StateLevelCountValidator

## Requirements: 
- Please update to include ALL locations globally. There is an internal API , pull data from it. 
- All clubs here: https://cde-assets-planetfitness.s3.amazonaws.com/locations.json. 

## Approach: 

Above mentioned All CLubs API was not sufficient to get all data fields which has `pfx:clubs` as `id` and these IDs need to use in 
another internal API to pull all data fields. 

- First API : https://cde-assets-planetfitness.s3.amazonaws.com/locations.json  
- Parse `"id": "pfx:clubs:25411afd-c286-11e8-999a-a511d4663031",`
- reconstruct 2nd API URL by using `id` E.g., `https://www.planetfitness.com/gyms/pfx/api/clubs/pfx:clubs:25411afd-c286-11e8-999a-a511d4663031` 
- Parse all locator data from here 

## Note: 
- First API : `https://cde-assets-planetfitness.s3.amazonaws.com/locations.json`  
- New API Endpoint: `https://www.planetfitness.com/gyms/pfx/api/clubs/locations` this API endpoint is not valid now.  [ Dec 10, 2021]
- First API is valid now, `https://cde-assets-planetfitness.s3.amazonaws.com/locations.json`  [ Dec 10, 2021]

### Results: 
- Total Locations:  2192 as of May 12, 2021
- Total Locations:  2243 as of July 28, 2021
