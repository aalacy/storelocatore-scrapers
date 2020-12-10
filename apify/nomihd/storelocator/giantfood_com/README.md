# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py


use --ignore StreetAddressHasNumber as it's throwing error even streetAddress has number in it.

use --ignore StreetAddressHasStateName as it's throwing error even there's no stateName in the streetAddress




########################### VALIDATOR LOG ###################################
[7m[32m========== Validating data ==========[0m
[7m[34mChecking for schema issues (e.g. required columns, etc.)...[0m
[7m[32m========== Looks good! ==========[0m
[7m[34mChecking for blank cells in your dataset...[0m
[7m[32m========== Looks good! ==========[0m
[7m[34mEnsuring that we can infer country code for most of your records...[0m
[7m[32m========== Looks good! ==========[0m
[7m[34mChecking for garbage values (HTML tags, nulls, etc.)...[0m
[7m[32m========== Looks good! ==========[0m
[7m[34mChecking for centroid quality issues...[0m
[7m[32m========== Looks good! ==========[0m
[7m[34mEnsuring that all street addresses have an address number...[0m
[7m[31m!!!!!!! Ignoring StreetAddressHasNumber !!!!!!![0m
[7m[34mEnsuring that street addresses do not have a state name in them...[0m
[7m[31m!!!!!!! Ignoring StreetAddressHasStateName !!!!!!![0m
[7m[34mValidating consistency of geography columns...[0m
[7m[32m========== Looks good! ==========[0m
[7m[34mValidating country-specific information (states, zip codes, phone #'s)...[0m
[7m[32m========== Looks good! ==========[0m
[7m[34mEnsuring that store number column is totally filled and unique or totally empty...[0m
[7m[32m========== Looks good! ==========[0m
[7m[34mChecking the number of POI in your data against our internal truthset...[0m
[7m[32m========== Looks good! ==========[0m
[7m[34mEvaluating the number of POI in your data by state compared to our truthsets...[0m
[7m[32m========== Looks good! ==========[0m
[7m[34mChecking that each column has adequate fill rate...[0m
[33m69.24528301886792% of column phone is <MISSING> or <INACCESSIBLE>. Are you sure you scraped correctly?[0m
[7m[34mChecking for duplicate identity rows...[0m
[31mFound 1 duplicate rows in the data. Each example below is a row that exists at least twice in the dataset:
     location_name             street_address       city state    zip country_code location_type
516  Shell Station  24851 JOHN J WILLIAMS HWY  MILLSBORO    DE  19966    <MISSING>   GAS_STATION
[0m
This check is not ignorable.
[7m[34mChecking for <lat, lngs> with multiple addressess...[0m
[7m[32m========== Looks good! ==========[0m
[7m[34mChecking for addresses that have multiple <lat, lngs> associated with them...[0m
[33mWARNING: We found 1 cases where a single address has multiple <lat, lngs>. Are you sure you scraped correctly? Examples:
                street_address  same_lat_count  same_lng_count
174  24851 JOHN J WILLIAMS HWY               1               2
[0m
[7m[34mLooking for common scraping mistakes...[0m
[33mWARNING: The number of rows in your data (530) is a multiple of 10. This is sometimes an indication that you didn't correctly paginate through the results on the store locator, though it could also just be a coincidence. Please review the website once more to make sureyou're scraping correctly![0m
[7m[37m
============= Results =============[0m
[7m[32m======== 11 checks passing ========[0m
[7m[33m======== 0 checks ignored ========[0m
[7m[36m======== 3 checks warning ========[0m
[7m[31m======== 1 checks failing ========[0m
[7m[37m===================================
[0m
[7m[33mClose! You still have 1 check(s) that need to pass.[0m

##############################################################################
