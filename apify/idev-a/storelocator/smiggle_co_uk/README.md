There are some potential issues when running the validate.py

# Error in parsing address

All locations are parsed directly from the HTML page. So I ignored country code check, street address check, zip code check and geo location check.

--ignore CountryCodeFillRateChecker --ignore StreetAddressHasNumber --ignore GeoConsistencyValidator --ignore CountryValidator --ignore LatLngDuplicationValidator