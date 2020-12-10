# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore StreetAddressHasNumber --ignore StreetAddressHasStateName

47   20 Court House South Dennis Rd., Court House V...  ADDR_HAS_NO_NUMBER         47
86                176-60 Union Turnpike, Utopia Center  ADDR_HAS_NO_NUMBER         86
91                      1 Fordham Plaza, Fordham Plaza  ADDR_HAS_NO_NUMBER         91
97               700 Broadway, Westwood Shopping Plaza  ADDR_HAS_NO_NUMBER         97
101            120A Dorman Center Drive, Dorman Center  ADDR_HAS_NO_NUMBER        101
7              1336 Bristol Pike, Woodhaven Mall SC  ADDR_CONTAINS_STATE_NAME          7
14  1103 W Baltimore Pike, Promenade at Granite Run  ADDR_CONTAINS_STATE_NAME         14
39                1933 Route 35 S, Allaire Plaza SC  ADDR_CONTAINS_STATE_NAME         39
41            1515 Rte. 22 West, Tjmaxx Of Watchung  ADDR_CONTAINS_STATE_NAME         41
57        100 Pocono Commons, TJMaxx of Stroudsburg  ADDR_CONTAINS_STATE_NAME         57

data from API

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
