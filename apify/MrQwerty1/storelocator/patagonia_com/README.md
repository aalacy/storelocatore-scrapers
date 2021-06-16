# How to write a Python3 scraper for SafeGraph (Simple)


Checked myself, data is valid: --ignore StreetAddressHasStateName --ignore StateLevelCountValidator

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py


## R&D By Faruque 

I have updated the code and found `4117` stores

Found `87` stores from [store-locator](https://www.patagonia.com/store-locator)

And rest from the internal [api](https://patagonia.locally.com/stores/conversion_data)

> as it is Global data and so it had to ignore by some validator flags , checked myself data WAS valid 