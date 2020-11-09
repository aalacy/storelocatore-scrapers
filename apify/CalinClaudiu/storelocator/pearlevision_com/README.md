# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore StreetAddressHasNumber --ignore StreetAddressHasStateName


                                 street_address              REASON  rowNumber
13            26 airport square shopping center  ADDR_HAS_NO_NUMBER         13
139  naval submarine base new london, bldg. 484  ADDR_HAS_NO_NUMBER        139
228   navy air station north island, bldg. 2017  ADDR_HAS_NO_NUMBER        228
245                                   <MISSING>  ADDR_HAS_NO_NUMBER        245
258          carretera 172 esquina 787 local 22  ADDR_HAS_NO_NUMBER        258


260   rexville town centre rd. 167 km 17.6  ADDR_CONTAINS_STATE_NAME        260
265  carretera pr #1 y int # 172, local 17  ADDR_CONTAINS_STATE_NAME        265


Data grabbed from API. Could parse these specific cases, but data is pulled accurately.




Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
