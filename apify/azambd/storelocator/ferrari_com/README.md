
# Scraping Requirements: 

Crawl was incomplete for the US even before faiilng. When you fix (or rewrite), please correct that and also include ALL locations globally. All data can be found here (and doesn’t require sgzip): https://www.geocms.it/Server/servlet/S3JXServletCall?parameters=method_name%3DGetObject%26callback%3Dscube.geocms.GeoResponse.execute%26id%3D1%26idLayer%3DD%26licenza%3Dgeo-ferrarispa%26progetto%3DFerrari-Locator%26lang%3DALL&encoding=UTF-8

# Note: 
As it included all locaitons globally, so there is no SUCCESS file and validated the Data. 


# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

