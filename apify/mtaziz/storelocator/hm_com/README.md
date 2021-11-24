# Required Memory to run the crawler 

The cralwer has particular memory requirement as this crawler uses `sgpostal`, While running this crawler, we need to make sure that the allocated memory on running instance is higher than 4096 MB . If the allocated memory happens to be lower than 4096 MB, the crawler is likely to fail to run with SUCCESS. 

# Validation Issues:
The followed validation tests ignored:


- `--ignore CountryCodeFillRateChecker`
- `--ignore CentroidValidator`
- `--ignore StreetAddressHasNumber`
- `--ignore StreetAddressHasStateName` 
- `--ignore GeoConsistencyValidator` 
- `--ignore CountryValidator` 
- `--ignore StoreNumberColumnValidator`
- `--ignore CountValidator` 
- `--ignore StateLevelCountValidator`
- `--ignore LatLngDuplicationValidator`

Still one checks is failed ( `LatLngDuplicationValidator`)


