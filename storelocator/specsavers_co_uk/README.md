# All locations are in UK. So I ignored country code check and zip code check.

--ignore CountryCodeFillRateChecker --ignore CountryValidator

# All street addresses are parsed directly from API response and the HTML page. So I ignored street address check and geo code check.

--ignore StreetAddressHasNumber --ignore GeoConsistencyValidator 

# Some locations are parsed from HTML page and have no store numbers. So I ignored store number check.

--ignore StoreNumberColumnValidator 