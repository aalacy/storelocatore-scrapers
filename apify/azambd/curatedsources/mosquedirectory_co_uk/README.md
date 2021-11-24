# How to write a Python3 scraper for SafeGraph (Simple)


Checked myself, data is valid: --ignore StreetAddressHasStateName --ignore StateLevelCountValidator

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

## Description
Please crawl mosquedirectory.co.uk (approx 2.4K locations). You can start on https://www.mosquedirectory.co.uk/browse/, or search by zip on homepage. 

Populate location_type with the "type" field on the page (E.g., location_type would be "Masjid/Mosque" from <span class="tag-masjid"> on page_url https://www.mosquedirectory.co.uk/mosques/england/london/barking-and-dagenham/eastbury/Masjed-e-Umar-Barking-and-Dagenham-Essex-London/3396

## Possible Approach: 

 - I did not see any internal API 
 - Parsed data from HTML markup 
 - Used Multi-threads concurrent futures

 > latitude , longitude and Hours of operations were not available 
 > Total Location Found = 2239

 ### Duplicate by validator: [Same Location Name but different page_url] Example
 - Holloway Mosque : https://www.mosquedirectory.co.uk/mosques/england/london/islington/holloway/Holloway-Mosque-Holloway-Islington-London/1130
 - Holloway Mosque : https://www.mosquedirectory.co.uk/mosques/england/london/islington/holloway/Holloway-Mosque-Holloway-Islington-London/2711

> SUCCESS file is not possible because of Checking for duplicate identity rows...