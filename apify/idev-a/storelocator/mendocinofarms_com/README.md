# All data is parsed from the json in the HTML page and they are all matched to the information on the site. So I ignored street address check.

--ignore StreetAddressHasNumber 

# All locations are parsed from the location list page so I ignored location count check and state check.

--ignore CountValidator --ignore StateLevelCountValidator 