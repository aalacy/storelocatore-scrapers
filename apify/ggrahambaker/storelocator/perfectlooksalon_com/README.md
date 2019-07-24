# How to write a Python3 scraper for SafeGraph

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py


# site to scrape: needs to scrape a few different state url to get all locations
locator_domain = 'https://www.perfectlooksalons.com/' 

ext_arr = ['/family-haircare/alaska/', 'family-haircare/arizona/', 'family-haircare/idaho/', 'family-haircare/oregon/', 'family-haircare/washington/']



