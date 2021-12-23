# sonicdrivein.com crawler

## Description

Please write a crawler to scrape store locations from sonicdrivein.com.

## Info:

- All locations in USA
- On screen parsing is not working, it will give 504
- Must use Internal API Endpoint : https://maps.locations.sonicdrivein.com/api/getAsyncLocations?template=search&level=search&search=99701
- Use Dynamic sgzip
- Total Locations ~3057

Another example: https://maps.locations.sonicdrivein.com/api/getAsyncLocations?template=search&level=search&search=78249

## R&D:

Using concurrent approach and pulling `25503` zip codes I found`3544`stores in `~2650s`
