# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py


# Scraper Development Requirements: 

Please crawl datacenters.com for `US`, `CA` & `GB`, accessible from this API endpoint: 

- USA API Endpoint URL  <https://www.datacenters.com/api/v1/locations?query=united%20states&withProducts=false&showHidden=false&nearby=false&radius=0&bounds=&circleBounds=&polygonPath=&forMap=true>

- Canada API Endpoint URL = <https://www.datacenters.com/api/v1/locations?query=canada&withProducts=false&showHidden=false&nearby=false&radius=0&bounds=&circleBounds=&polygonPath=&forMap=true>

- Canada API Endpoint URL = <https://www.datacenters.com/api/v1/locations?query=united%20kingdom&withProducts=false&showHidden=false&nearby=false&radius=0&bounds=&circleBounds=&polygonPath=&forMap=true>

## Notes about fields/column mapping
For the `location_name`, instead of using the `name` field in the API, please use a combination of `providerName` & the words `Data Center` e.g., `Digital Realty Data Center`.

## Estimated Counts 
Estimated Counts: 1,265 US locations, 86 Canada locations, and 119 GB locations

## `location_name` fixing

Some of the `providerName's` had `Data Center` in them already so now there is `NTT Global Data Centers Data Center`. `Data Center` will be appended if only it does not exist in the `location_name` or in another word, if `Data Center` or `Data Centers` is not found in the `providerName`?

## Store Number ( `store_number`)

Instead of using the `providerId` for the `store_number`, please use `id`; `providerid` is not unique as it is for all locations for that provider (e.g., all of NTT Global’s locations)

## NOTE: Running crawler on production env and memory requirements 
It is found that whenever `sgscrape.sgpostal` used in the `scraper` , with RAM/ memory ( 1024 MB or 2048 MB ) scraper is likely to fail to run on the production environment. However, 4096 MB memory found to be working without any issue. 