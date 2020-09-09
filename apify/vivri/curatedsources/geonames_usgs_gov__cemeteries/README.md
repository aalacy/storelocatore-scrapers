## Purpose
- This scraper fetches cemeteries from the Geonames USGS service.

## Caveats
- The scraper takes over 8h, and the `data.csv` file has been generated on a dev machine and manually passed to Mia Litman.
- The data has more holes in it than usual, owing to the fact some old cemeteries don't have road access.
    - The guaranteed fields are:
      - locator_domain 
      - page_url
      - location_name
      - country_code
      - store_number
      - location_type
      - latitude
      - longitude
