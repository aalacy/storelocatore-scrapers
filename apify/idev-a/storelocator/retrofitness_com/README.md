There are some potential issues when running the validate.py

# Error in parsing address

All locations are parsed directly from the HTML page and count is correct. So I ignored location count check.

--ignore CountValidator

# There aren't any locations in North Carolina now so I ignored state count check.

--ignore StateLevelCountValidator