There are some potential issues when running the validate.py

# Error in parsing latitude

All geo locations are parsed directly from the HTML page. So I ignored geo location check.

--ignore CentroidValidator

# Charlottesville' phone number is "434-97-PIZZA  (74992)" on the site. So I ignored phone number check.

--ignore CountryValidator