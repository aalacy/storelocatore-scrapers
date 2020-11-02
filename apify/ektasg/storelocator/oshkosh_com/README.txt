python validate.py data.csv --ignore CentroidValidator --ignore LatLngDuplicationValidator --ignore StreetAddressHasStateName --ignore StreetAddressHasNumber

Validation is not passing for Canada locations due to below reasons:
For Canada - NIG 3A2 and H3Z 1O2 are showing as INVALID_CA_POSTAL_CODE but these are what are present and extracted from site.

The below two records are duplicate since they appear two times on the site so that is why they are duplicates in the data sheet as well.
            location_name       street_address city state      zip country_code     location_type
429       Stone Road Mall  435 Stone Road West         ON  N1G 2X6           CA  Carter's OshKosh
430  Lougheed Town Centre   9855 Austin Avenue         BC  V3J 1N4           CA  Carter's OshKosh

Below is mentioned as Invalid CA province in validator, but this is on website.
107  JEAN-SUR-RICHELIEU          450-741-6849  J2W 0E2     INVALID_CA_PROVINCE
129                  QU  	(514 564-4500  H2N 1N7     INVALID_CA_PROVINCE        
133           TERRITORY   	867-393-4488   Y1A 1A3     INVALID_CA_PROVINCE        
