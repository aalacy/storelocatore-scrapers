# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore StreetAddressHasNumber --ignore StoreNumberColumnValidator

78                                 3A Peninsula Center  ADDR_HAS_NO_NUMBER         78
87                       2000 El Camino Real, Suite 15  ADDR_HAS_NO_NUMBER         87
196  Detroit Metropolitan Wayne County Airport, Nor...  ADDR_HAS_NO_NUMBER        196


196    MI  <MISSING>  482424    INVALID_US_ZIP        196

https://modpizza.com/locations/dtw-airport/
Zip is exactly incorrect on website..
48242 would be correct.. hard-coded change.

Store number column is only partially filled. Please make sure you're capturing store numbers for all POI on the st


Data grabbed from API, confirmed it's correct.


Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
