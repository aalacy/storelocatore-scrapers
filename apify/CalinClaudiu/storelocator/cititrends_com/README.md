# How to write a Python3 scraper for SafeGraph (Simple)

validate.py data.csv --ignore StreetAddressHasNumber --ignore StreetAddressHasStateName 


--ignore StreetAddressHasNumber
      street_address              REASON  rowNumber
22  610--15th Street  ADDR_HAS_NO_NUMBER         22

--ignore StreetAddressHasStateName
                street_address                    REASON  rowNumber
349  3600 Gus Thomasson Ut 124  ADDR_CONTAINS_STATE_NAME        349
483  1100 N Miami Blvd, St 135  ADDR_CONTAINS_STATE_NAME        483
548  3200 S Lancaster, St 170D  ADDR_CONTAINS_STATE_NAME        548

--ignore GeoConsistencyValidator

47   19701   Delaware  ZIPCODE_NOT_IN_STATE         47
48   19904   Delaware  ZIPCODE_NOT_IN_STATE         48
49   19802   Delaware  ZIPCODE_NOT_IN_STATE         49
372  53144  Wisconsin  ZIPCODE_NOT_IN_STATE        372
373  53405  Wisconsin  ZIPCODE_NOT_IN_STATE        373

This above is due to sgvalidator not recognizing the following states:

←[7m←[34mValidating country-specific information (states, zip codes, phone #'s)...←[0m
←[31mFound 9 concerning rows. Examples:
         state           phone    zip            REASON  rowNumber
47    Delaware  (302) 834-1505  19701  INVALID_US_STATE         47
48    Delaware  (302) 674-2246  19904  INVALID_US_STATE         48
49    Delaware  (302) 762-5694  19802  INVALID_US_STATE         49
372  Wisconsin  (262) 657-1695  53144  INVALID_US_STATE        372
373  Wisconsin  (262) 598-8675  53405  INVALID_US_STATE        373
←[0m
This check is not ignorable.

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py
