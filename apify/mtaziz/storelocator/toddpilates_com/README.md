# How to write a Python3 scraper for SafeGraph (Simple)

Note: This template differs from the older `python3` template in that you don't need to worry about javascript related files such as `scrape.js` and `package.json`. This template also builds faster if you're testing it in a local docker image.

Please write your scraper such that running `scrape.py` produces a file `data.csv` containing the scraped data.

Remember to update `requirements.txt` with all dependencies needed to run your scraper. 
Please make sure that:
* Your scraper can be run successfully by executing https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/run_scraper.sh 
* The resulting output passes https://github.com/SafeGraphInc/crawl-service/blob/master/scripts/validate.py

# Skip method did not work

```
skip_num_start = 0
skip_num_end = 900  # After 800 it does not yield the data, considering future data, 900 seems to be ideal choice
for skip_num in range(skip_num_start, skip_num_end):
    url_api = f"https://www.carpetone.ca/carpetone/api/Locations/GetClosestStores?skip={skip_num}&zipcode=M4B&latitude=56.130366&longitude=-106.346771"
```

- Example URL considering `skip_num=0`
https://www.carpetone.ca/carpetone/api/Locations/GetClosestStores?skip=0&zipcode=M4B&latitude=56.130366&longitude=-106.346771

This would return the results for 3 stores - from front end on website search for each search query using zip code returns only 3 results. There are few chanllenges are involved with this scraper:

1) While search Canadian Zip code it returns US store information
2) I have tried with statically generated 100 zip codes in Canada considering 100Miles radius, most of the stores returned by the search results belong to the US. That's why we did not get expected store count 83 
Maximum we got using `skip_num`  method was 62. 
3) Changing `zipcode` along with corresponding `latitude` and `longitude` were failed to return the expected results, 
4) `skip_num` was kept same but `zipcode` with corresponding `latitude` and `longitude` were changed - no luck 
5) Using `sgselenium` with 100 zip codes were failed to yield expected store counts. lot of zipcode does not return the results
6) NOTE: I will other trial methods applied on it later on 

Solution: 
Google tag manager URL contains 952 Store URLs. 
Test & scraping is underway for this. I will update the final results as soon as it is done. 