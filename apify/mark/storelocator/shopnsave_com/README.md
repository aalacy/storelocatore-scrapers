# How to write a JavaScript scraper for SafeGraph using Apify

Please write your code inside scrape.js at the `// Replace this with your actual scrape` comment. 

Your logic will run agianst every URL in the RequestList. Note that you can use a RequestQueue instead of a RequestList if this scrape requires URLs to be generated dynamically (https://sdk.apify.com/docs/api/requestqueue).

Documentation on using the BasicCrawler: https://sdk.apify.com/docs/api/basiccrawler

Executing `apify run` should create an apify_storage directory with json objects for all of the POI you scraped. If you don't have the apify CLI, running `npm install` should install it. Documentation for the CLI is here: https://github.com/apifytech/apify-cli

