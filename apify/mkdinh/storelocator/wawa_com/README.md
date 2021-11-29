# How to write a Node.js scraper for SafeGraph using the Apify PuppeteerCrawler in Stealth Mode

You can start writing your scraper in scrape.js between `// Begin scraper` and `// End scraper` comments.

Your logic will run agianst every URL in the RequestQueue. See https://sdk.apify.com/docs/api/requestqueue

Documentation on using the PuppeteerCrawler: https://sdk.apify.com/docs/examples/puppeteercrawler

Apify test account information:
Token: iZH7QL3aoPb3wvq9TdkJFRDLC

Running the crawler with proxy enabled:
`apify init && USE_PROXY=true APIFY_PROXY_PASSWORD=HKT2ZAHSvokX3hLibngLgo5nT apify run --purge`

Remember to update `package.json` with all dependencies needed to run your scraper.
Please make sure that:

- Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh
- The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
