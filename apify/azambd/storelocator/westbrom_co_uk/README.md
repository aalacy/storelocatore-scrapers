# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

## Description
This is a rewrite.
Please crawl westbrom.co.uk. Include Branches & Agencies (if applicable)

## Note: 
UK zip codes using in the locator https://www.westbrom.co.uk/customer-support/branch-finder  and get the locations needs selenium, but sgselenium did not work. 
I have tested and found selenium worked fine. Most probably `https` must needs but sgselenium did not able to load `https` [ showed 'Not Secure'] 

I have found an alternative data source : `https://www.bankopeningtimes.co.uk/west-bromwich-building-society/west-bromwich-building-society.html`  and from here I pulled 
all location page urls of westbrom.co.uk, and parse data 

## R&D: 
Total valid locations 34, Three pages are broken: 

 `https://www.westbrom.co.uk/customer-support/branch-finder/birmingham`
 `https://www.westbrom.co.uk/customer-support/branch-finder/merry-hill` 
 `https://www.westbrom.co.uk/customer-support/branch-finder/west-bromwich-dartmouth-square`
