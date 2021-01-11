There are some potential issues when running the validate.py

# All information is parsed directly from the HTML page so I ignored ZIPCODE_NOT_IN_STATE error.

--ignore GeoConsistencyValidator

# There are 2 different services in one geo location, but their street addresses are different. So I ignored geo duplication check.

--ignore LatLngDuplicationValidator