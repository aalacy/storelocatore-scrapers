# How to write a Python3 scraper for SafeGraph (Simple)
validate.py data.csv --ignore StreetAddressHasNumber --ignore CountryValidator


83                        8310 Mills Drive, Suite 8310  ADDR_HAS_NO_NUMBER         83
280  6020 Jericho Turnpike, In The Dicks Sporting G...  ADDR_HAS_NO_NUMBER        280
Data scraped correctly from API

363    SC  2191140  292123730  INVALID_US_ZIP        363
Data scraped correctly from API


Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
