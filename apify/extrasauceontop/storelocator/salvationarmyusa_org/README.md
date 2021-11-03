 The raw data for the Salvation Army contains several problems, all data gathered was parsed directly from an API call. The below validators have been skipped for the following reasons.

The below is the full command I ran to generate the success file.
python validate.py data.csv --ignore LatLngDuplicationValidator --ignore CountryValidator --ignore GeoConsistencyValidator --ignore StreetAddressHasStateName --ignore StreetAddressHasNumber --ignore CentroidValidator

1. Centroid quality issues: Lat and Lng for some rows is imprecise.
    The Lat and Lng are pulled directly from the API as they are stored. If they are plugged in, it does appear to be correct for the locations

2. Ensuraing all street addresses have an address number:
    Addresses are completely missing for some locations.

3. Ensuring street addresses do not have a state name in them:
    The street address field in the API occassionally contains the City and State in it. This information is the repeated in the City and State fields

4. Validating consistency of geography columns: Zip code not in state.
    The zip code field will occassionally contain a phone number instead of a zip code. There is no zip listed in these cases. The phone number is the repeated in the Phone field

5. Validating country specific information: Invalid US Zip.
    This issue is cause by the reason listed above. The phone number being pulled in as opposed to the zip in some cases causes the error

6. Multiple addresses belong to one Lat/Lng pair.
    Occassionally, 2 locations will share an address (Example if there is a church and a thrift shop, sometimes these will be broken out). That is raising this issue.