Checks ignored to generate success file

1. CountryCodeFillRateChecker
    This check was skipped because the country is not the US or Canada, per the output message from the check

2. LatLngDuplicationValidator
    Some locations are listed with the same lat/lng because they are either in the same building, or they are next to each other it seems.

The full command to generate the SUCCESS file is: python validate.py data.csv --ignore LatLngDuplicationValidator --ignore CountryCodeFillRateChecker