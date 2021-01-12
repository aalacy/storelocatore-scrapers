There are some potential issues when running the validate.py

# Error in parsing address

All locations are parsed directly from the HTML page and API response and count is correct. So I ignored street address check, location count check.

--ignore StreetAddressHasNumber --ignore CountValidator

# There are some locations in Canada, Mexico and Panama and that causes error in geo location check and zip & state check. So I ignored them.

--ignore GeoConsistencyValidator --ignore CountryValidator

# There aren't any locations in these states: 'WI', 'OR', 'MN', 'MD', 'IL' now so I ignored state count check.

--ignore StateLevelCountValidator