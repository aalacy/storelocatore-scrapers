# How to write a Python3 scraper for SafeGraph (Simple)


Checked myself these 2 different stores 
>Checking for <lat, lngs> with multiple addressess...
>Found 1 <lat, lng> pair(s) that belong to multiple addresses. Examples:
>      latitude    longitude                                    street_address  num_addrs
>151  37.248199  -121.802654  {5730 Cottle Rd. #120, 5730 Cottle Rd. Ste. 120}          2

* 1. https://www.hawaiianbarbecue.com/locations/san-jose-cottle/ 
* 2. https://www.hawaiianbarbecue.com/locations/south-san-jose/

Store is valid: 
> Examples of states that we saw in your data but didn't expect to see: ['VA'].
* https://www.hawaiianbarbecue.com/locations/chesapeake/ 


Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

