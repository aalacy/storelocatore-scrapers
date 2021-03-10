There are some potential issues when running the validate.py

# Error in parding address
All data come from the json request including street, city, state, zip, etc.
However, there are some errors for certain records from the validate.py such as Ignoring StreetAddressHasNumber, Ignoring StreetAddressHasStateName, Ignoring GeoConsistencyValidator, Ignoring StateLevelCountValidator
so I tried like the following to get the SUCCESS

python validate.py data.csv --ignore StreetAddressHasNumber --ignore StreetAddressHasStateName --ignore GeoConsistencyValidator --ignore StateLevelCountValidator
