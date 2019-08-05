# How to write a Node.js scraper for SafeGraph using the Apify BasicCrawler

You can start writing your scraper in scrape.js between `// Begin scraper` and `// End scraper` comments. 

Your logic will run agianst every URL in the RequestList. Note that you can use a RequestQueue instead of a RequestList if this scrape requires URLs to be generated dynamically (https://sdk.apify.com/docs/api/requestqueue).

Documentation on using the BasicCrawler: https://sdk.apify.com/docs/api/basiccrawler

Remember to update `package.json` with all dependencies needed to run your scraper.
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
