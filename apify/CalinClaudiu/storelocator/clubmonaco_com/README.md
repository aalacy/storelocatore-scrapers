# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore StreetAddressHasNumber --ignore CountryValidator --ignore LatLngDuplicationValidator

3         1225 Third Street Unit 1225  ADDR_HAS_NO_NUMBER          3
31  Route 24 and JFK Parkway Unit 232  ADDR_HAS_NO_NUMBER         317
41    CT  (203) 6293529  6830  INVALID_US_ZIP         41
24  40.713811  -74.017671  {250 Vesey Street Suite 208, 250 Vesey Street ...          2
48   43.72467  -79.455363  {157 Bloor Street West, 3401 Dufferin Street #...          2

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
