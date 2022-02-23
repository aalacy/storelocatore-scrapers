# aldi.com.au crawle

## Description

Please crawl aldi.com.au for locations in Australia (581 stores per locator url). It appears that the lat & long values are reversed; if this is how they are provided by the site/API though let me know.

## Info:

Locator : https://storelocator.aldi.com.au/Presentation/AldiSued/en-au/Start

## R&D

Pretty complex project

Got `580` locations from `57600` url in `~20m`. Used concurrent approach for speed up.

Make the whole location into `240*240` squared and find in each box

Store Url = `https://www.yellowmap.de/Presentation/AldiSued/en-AU/ResultList?Lux={}&Luy={}&Rlx={}&Rly={}`

### MISSING FIELDS

- phone
- location_type
- state (most locations)
