# Validation issues
I'm using usaddress library to parse address, so might be some issues with that. Some of the addresses can't be parse with the library in this case I add whole string as street_address
1. --ignore StreetAddressHasNumber, ADDR_HAS_NO_NUMBER
2. --ignore StreetAddressHasStateName, ADDR_CONTAINS_STATE_NAME
3. --ignore CountValidator, 1120 POI, but your file has 931 POI
4. --ignore StateLevelCountValidator
6. --ignore LatLngDuplicationValidator, 40.985566  -111.89237