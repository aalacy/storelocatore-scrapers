# How to write a Python3 scraper for SafeGraph

### Run `validate.py` with these flags to pass:
    * --flag1 (Reason for flag1)
    * --flag2 (Reason for flag2)
    * ...

### Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
* Generate like so: https://github.com/SafeGraphCrawl/crawl-service/blob/master/docs/cookbook/reqfile.md

### Make sure to run your scraper in Docker and validate the results:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
