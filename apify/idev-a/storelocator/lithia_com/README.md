There are some potential issues when running the validate.py

# Error in parding address

"DCH Honda Dealerships" only gives information for state and coordinate, so just put <MISSING> in street_address and used the following argument to ignore street check.

--ignore StreetAddressHasNumber

# All data is parsed directly from the HTML DOM and the site has 215 stores. So I used the following arguments to ignore the count check and state count check.

--ignore CountValidator --ignore StateLevelCountValidator

# Some services like "Crater Lake Ford Lincoln Service" and "Crater Lake Lincoln Service" have same geo locations, but different names, so used following argument to ignore geo location check

--ignore LatLngDuplicationValidator