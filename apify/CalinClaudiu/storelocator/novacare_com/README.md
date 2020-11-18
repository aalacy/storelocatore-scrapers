# How to write a Python3 scraper for SafeGraph (Simple)
validate.py data.csv --ignore CentroidValidator --ignore StreetAddressHasNumber --ignore StreetAddressHasStateName --ignore StoreNumberColumnValidator --ignore LatLngDuplicationValidator

927            182 Boulevard  ADDR_HAS_NO_NUMBER        927
955  3 Bethesda Metro Center  ADDR_HAS_NO_NUMBER        955

331  2751 O'Varsity Way, Room 265, University Of Ci...  ADDR_CONTAINS_STATE_NAME        331

←[31mSome (n = 1762) of your store numbers contain invalid characters. Store numbers should only contain numbers or lett
ers, not any special characters: ['477d66d3-b1e4-4a4b-9072-a94bcbeb95e8'
 '9c4a88e7-871c-482f-909f-0755a1ecb390'
 '501c0d5f-ba2b-4c92-ab6f-98f999e708e1'
 '7de2ab74-9818-4288-9486-d8883714d689'
 '3696ad5a-8534-4cd4-96be-e944b5f5ec6e']←[0m


Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
