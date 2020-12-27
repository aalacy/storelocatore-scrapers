# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore CountryValidator --ignore StreetAddressHasNumber


2    NC  704â€‘982â€‘6060  28001  INVALID_US_PHONE          2
4    NC  910â€‘436â€‘4090  28390  INVALID_US_PHONE          4
5    NC  919â€‘639â€‘5813  27501  INVALID_US_PHONE          5
6    NC  919â€‘303â€‘5148  27502  INVALID_US_PHONE          6
7    NC  336â€‘434â€‘3131  27263  INVALID_US_PHONE          7

Validator had a drink. I don't see these characters.




Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
