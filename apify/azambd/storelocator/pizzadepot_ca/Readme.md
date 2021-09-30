# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py


## R&D:

- Page loading has problem while crawling. It fixed. 
- Total Locations: 31 as of 21st July, 2021 
- `store_number` is missing 
- HOO is missing for 2 locations: `https://www.pizzadepot.ca/2114-albert-st-regina/` and `https://www.pizzadepot.ca/3373-28a-ave-nw-edmonton/` as of 28th July 2021
