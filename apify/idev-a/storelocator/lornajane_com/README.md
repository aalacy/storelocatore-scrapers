There are some potential issues when running the validate.py

# --ignore CountryValidator
There is one location with invalid phone # from the json data.
For example, 39496400623.

# --ignore CountValidator
Actually 26 locations come from json, but it has some duplication.
After filter them out, it will be 20.

# --ignore StateLevelCountValidator
All data count would be fine from json.
