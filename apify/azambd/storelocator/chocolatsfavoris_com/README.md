# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py


## Info:

This is a rewrite of SLC-31323 .
The issue was, "The previous script didn't work out due to lots of markers overlapped each other and as a result, it is not possible to click each marker to get the location detail."

## R&D: 
I changed the approach and pull data from Google API which APYKEY is available in the intenral source code. Script pulls APIKEY & each place_id dinamically from webpage
and pull data from Google API.  `f"https://maps.googleapis.com/maps/api/place/details/json?place_id={location['placeId']}&key={api_key}"`