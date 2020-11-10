# Validation issue
1. --ignore StreetAddressHasStateName, row 115, ADDR_CONTAINS_STATE_NAME
2. --ignore GeoConsistencyValidator, row 139, ZIPCODE_NOT_IN_STATE
3. --ignore CountValidator, 293 POI, but your file has 257
4. --ignore StateLevelCountValidator
5. --ignore LatLngDuplicationValidator, <lat, lng> pair(s),  43.69391  -79.77079