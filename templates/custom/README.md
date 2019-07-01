# How to write a custom Node.js scraper for SafeGraph

You can write your scraper in scrape.js between `// Begin scraper` and `// End scraper` comments. 

Please use this template if you do not wish to interact directly with the Apify SDK. Just make sure that your `scrape()` function returns an array of objects representing the scraped store locator records.

Remember to update `package.json` with all dependencies needed to run your scraper.
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
