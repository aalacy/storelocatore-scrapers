#Validation issues
1. --ignore StreetAddressHasNumber, some of the stores are missing street_address
2. --ignore GeoConsistencyValidator, ZIPCODE_NOT_IN_STATE (30671)
3. --ignore CountValidator, the spider makes serach requests with state code to get results. I added all states for USA and Canada. Total adresses for crawl is 348, expected 390
4. Fixed one postal code, input value "CAN8T 3K7", in results "N8T 3K7".

