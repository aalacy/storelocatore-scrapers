This scraper is complicated so I wanted to break it down a bit

1. The scraper initially hits this endpoint: "https://www.webster.edu/_resources/dmc/php/locations.php?datasource=locations&type=listing&returntype=json&       xpath=items%2Fitem&items_per_page=100&page=1&search_phrase=&isinternational%5B%5D=United%20States" to get a JSON response containing:

    1. page_url
    2. location_name
    3. city
    4. state
    5. country
    6. store_number

2. Then the scraper loops through the page URLs to attempt to get the Street Address, Phone, and Zip code. This data is placed inconsistently, making it difficult to grab. On top of that, they have a default address they put in (1103 Kingshighway) under the Contact Us section that I hard code <MISSING> when it is listed as the street address

3. The Lat, Lng, Hours, and Location Type are all missing.

4. There is a legacy website ((https://legacy.webster.edu/locations/) that has a map on it and would be MUCH easier to scrape, but my concern is that this website is no longer updated, so scraping it is no good. If I am wrong, please let me know.