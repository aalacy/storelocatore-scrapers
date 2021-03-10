This crawler get the data associated with all Salvation Army locations in Canada under the domain salvationarmy.ca

For validation I skipped three warnings for the below reasons.

1. StoreNumberColumnValidator
    The store numbers can repeat if the location has multiple location types listed. That is because there is a unique row for each location type and store number pair. There are no duplicate rows of store number and location type

2. CountryValidator
    The Zip code data is failing on 9 rows because it is not in a valid Canada zip format. This is how the zip data is presented and it was scraped correctly

3. LatLngDuplicationValidator
    There are multiple locations at 1 address. These locations are unique as they have unique location_types and location_names. The latitude and longitude for these locations in most cases is the same, but sometimes in can differ between two locations with the same address by less than a tenth of a degree. This difference is resulting in the error.
