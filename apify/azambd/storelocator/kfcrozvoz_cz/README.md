# Crawl kfcrozvoz_cz

## Description

Please crawl kfcrozvoz.cz for locations in Czech republic

## Info:

- source page https://kfc.cz/main/home/restaurants
- it has internal API Endpoint: https://kfcrozvoz.cz/ordering-api/rest/v2/restaurants/ but it needs Authorization: Bearer Token
- need to check if this Authorization: Bearer is dynamic or static
- if Authorization: Bearer is dynamic then we can easily pull it by sgselenium

## R&D:

There are `107` stores and took 2s to get stores. I tried the bearer token seems static. But need to check once more

### MISSING Fieds:

- location_type
- phone
- state
