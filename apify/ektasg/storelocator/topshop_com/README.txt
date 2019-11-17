python validate.py data.csv --ignore StreetAddressHasNumber --ignore StreetAddressHasStateName --ignore LatLngDuplicationValidator

Also please note that states are missing in the json and also address is stored very vaguely in the attributes like in city attribute sometimes state is there or even zipcode is there which we cannnot validate. We are retriving the data as it is stored in the site in corresponding attributes.
M1P 45P - This is giving INVALID_CA_POSTAL_CODE whereas it is mentioned the same way on the site.Due to only this error, SUCCESS file is not getting generated as validation is not passing.
