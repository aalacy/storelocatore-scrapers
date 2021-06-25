
# wyndhamhotels.com/wyndham crawler requires maintenance!

## Requirements: 

Please update this to include ALL Wyndham child brands GLOBALLY (8431 locations). Once this one is passing QA, I will assign the rest of the Wyndham Hotels children to you and you can copy the same code to those directories).  Safegraph will filter each crawl to their respective brand based on the location_name &/or location_type.

More details: 
All Locations (~8.4K) depends on how many broken URLs:
Api: https://www.wyndhamhotels.com/BWSServices/services/search/properties?recordsPerPage=501200&pageNumber=1&brandId=ALL&countryCode=

Would require reconstruction of page-url in order to grab all data, which might need some fiddling but it's doable.


## Possible approach to pull data: 

- Step #1. pull all 'propertyId' from https://www.wyndhamhotels.com/BWSServices/services/search/properties?recordsPerPage=501200&pageNumber=1&brandId=ALL&countryCode=

- Step #2. reconstruction of page-url 

-  "uniqueUrl": "microtel/albertville-alabama/microtel-inn-and-suites-of-albertville/overview",  is page_url

- HOO is  MISSING

- location_type: Hotel 

* locator_domain = 'wyndhamhotels.com/wyndham'
* store_number = propertyId
* page_url = website + uniqueUrl


> SUCCESS file is not possible because it blocked when ran locally, proxy also got 403 sometimes. Need to observe performance in production


