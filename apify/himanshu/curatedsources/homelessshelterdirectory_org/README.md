# How to write a Python scraper for SafeGraph

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

address contains state name,address contains state name,invalid zip and i checked all data is true for this site

## Note: 
The rewrite workflow actually doesn’t work for curated sources. We’re going to fix but in the meantime, you can just override the current code & publish under their directory. 