# How to write a Python3 scraper for SafeGraph

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py


# site to scrape: http://ladiesworkoutexpress.com/findAClub.asp


● You noticed that the site uses anti-scraping mechanisms such as Captchas, IP address checks, etc.
● You couldn’t get validation to pass due to the site itself having bad data.
● The scraper takes a long time to run (an estimated runtime would be appreciated in this
case)
● You did something custom such as using an alternate scraping framework (feel free to
document things like this at top-level under your ​username​ directory).
● Anything else you think would help a future maintainer.


