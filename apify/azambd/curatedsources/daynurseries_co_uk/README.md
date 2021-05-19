# How to write a Python3 scraper for SafeGraph (Simple)

Validate needs --ignore CountryCodeFillRateChecker because store locator is from UK other than the US or CA

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

# Scraper Development Requirements:

Please crawl daynurseries.co.uk (approximately 12K total).  A few specifics:

1. For the location_name, truncate the portion after "at" e.g., for page_url https://www.daynurseries.co.uk/daynursery.cfm/searchazref/65432219576 , the location_name would just be "Bright Horizons" (NOT "Bright Horizons at 24 St Swithin"

2. Please add a NEW column to just this crawl called `brand_website`. E.g., for that same page_url provided above, this would come from https://www.brighthorizons.co.uk/our-nurseries/24-st-swithin-early-learning-and-childcare?utm_source=daynurseries.co.uk&utm_medium=Referral&utm_campaign=24StSwithin. (If you are able to truncate this so it is just the top-level domaine.g.,brighthorizons.co.uk that is preferred, but not required).

## Challenges:

The website has Incapsula Security, so it is complex

brand_site redirects as outbound that needs to bypass Incapsula too

phone is not available on-page, it needs to click on an Incapsula secured link and parse from the popup

sitemap page is also secured, and it needs cookies if it gets too many hits [ I observed it when I was testing ]

In order to subdue Incapsula Security, I had to use sgselenium which is slow from my pc, didn't pull all rows in a test run.

## Possible roadmap 

* I haven't found any internal API Endpoint to pull data from. 
* It may need to parse data from webpage [ screen scraping ]
* Instead of using website search function, and get through each page , it is good to use Sitemap 

### Sitemap: 
 https://www.daynurseries.co.uk/sitemaps/profile.xml 

 * The requirements/schema is basicaly the same. 

 > All data fields are available in detail page: https://www.daynurseries.co.uk/daynursery.cfm/searchazref/65432219576 , we need here one *extra field*, which is `brand_website` 

 * brand_website: 
 it needs to capture the final destination of this https://www.daynurseries.co.uk/externalsite.cfm?searchazref=65432219576&linkcategory=daynursery  [ it is redirecting to https://www.brighthorizons.co.uk/our-nurseries/24-st-swithin-early-learning-and-childcare?utm_source=daynurseries.co.uk&utm_medium=Referral&utm_campaign=24StSwithin ] 
 please capture only top-level domain name from this redirection, that is: `brand_website` = brighthorizons.co.uk 

* store_number: 65432219576  [ capture it from detail page url ]

* hours_of_operation = Opening Days:Mon-Fri; Opening Hours:0745-1745; Closed:Bank Holiday
