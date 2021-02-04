1. Data gathering
    To crawl this site, the script needs to extract a URL for each store webpage from the store locator, and then iterate through those URLs to get store specific information

    To get these URLs, I am using a Swiss cheese method. This is because some US stores are left out of each search. Example: If you search with country=USA, you would think that would return all the stores in the U.S., but there are several stores that never had a country value attached to them, so they do not show. If you search by Lat, Lng, you run into the same problem. For this crawl, there are three different searches, and I am hoping that a call to each will end up gathering all the stores in the U.S.

    1. Country = USA search
        Here I set the country equal to USA, loop through all returned pages and get the URL to each store.

    2. Zip search.
        You can set the map bounds and call all stores within the region. to do so I got the coordinates for the Southwest and Northeast of the U.S. (Including Alaska and Hawaii) and pass them like so (field_geo_location_boundary%5Blat_north_east%5D=47.56&field_geo_location_boundary%5Blng_north_east%5D=69.44&field_geo_location_boundary%5Blat_south_west%5D=16.11&field_geo_location_boundary%5Blng_south_west%5D=-178.85) as query parameters. I then looped through the pages and gathered all the URLs

    3. All search.
        You would think that leaving all query parameters blank would return every store, but for some unknown reason, it does not. Stores will be left out at complete random and which stores are left out changes over time. I can find no rhyme or reason for this behavior. I use this as a comprhensive search to try to fill in any holes left from the others
    
    Thus the Swiss cheese model. Some stores are left out of each query, but by layering all three, I am able to get a list of all US stores.

2. Validate.py warnings skipped
    CountryValidator
        The phone number 626-710-0788 is flagged as not a valid US number, but this is the number listed on the website for a store in California

    GeoConsistencyValidator
        The Zip code 92830 is not in the US, but it is the zip code listed for a store in California

    StreetAddressHasStateName
        A street address on the site has CA (the state name) in it

    StreetAddressHasNumber
        There are about 80 street addresses that are missing. These are all flagged for not having a number

    CentroidValidator
        There are several rows that round their longitude to 1 decimal point, raising this flag
