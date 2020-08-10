# How to write a Python3 scraper for SafeGraph (Simple)

## Validation Caveats
- Use the following flags when running:
```shell script
 --ignore StreetAddressHasNumber --ignore LatLngDuplicationValidator --ignore StreetAddressHasStateName --ignore GeoConsistencyValidator --ignore StoreNumberColumnValidator
``` 
- Currently fails the identity check of the validator, since Windermere has multiple "offices" housed in the same street address. 

## Simple Scraper Pipeline Lib
- See `simple_scraper_pipeline.py` for a draft of a miniature pipeline library and useful toolset.