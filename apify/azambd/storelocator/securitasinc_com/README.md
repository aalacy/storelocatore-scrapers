No SUCCESS file!!

Multiple locations are duplicated but they have unique phone number and unique pages, discussed with Mia and that's okay.

## Example of unique page:
* https://www.securitasinc.com/contact-us/Arizona/Phoenix/
* https://www.securitasinc.com/contact-us/Arizona/Phoenix-Mobile/

## Example of same address , unique phone and page:
* 2790 N. Academy Blvd., Ste. 130
* https://www.securitasinc.com/contact-us/Colorado/Colorado_Springs/
* https://www.securitasinc.com/contact-us/Colorado/Colorado-Springs-Mobile/


Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
