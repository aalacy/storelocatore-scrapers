# How to write a Python3 scraper for SafeGraph (Simple)


Checked myself, data is valid: --ignore StreetAddressHasStateName --ignore StateLevelCountValidator

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py



## R&D: 
- Public api exists: https://apidocs.simon.com/?aspxerrorpath=/Errors/default.aspx#8ba76b29-2e3f-4814-a0f6-932433a5561a   from where all malls were extracted. Please note there is GET request to retrieve all malls, but it doesn't return HOO
- That is why additional call is used to retrieve information of the single mall based on ID
- 202 belongs to simon domain
- 88 location with missing lat,lng and hoo [ Mostly these are redirected to another domain]
- Dedupe on store_number

> Locations: 290 as of 30th March, 2022